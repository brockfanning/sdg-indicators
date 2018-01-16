// This is a proof-of-concept for using tidy data format and d3.js to visualize
// subnational data on maps.

var container = '#map-' + map_vars.indicator_id;
var svg = d3.select(container);
var width = +svg.attr('width');
var height = +svg.attr('height');
var path = d3.geoPath();

// This hardcoded list adapted from: https://gist.github.com/mbostock/4090846#file-us-state-names-tsv
// The idea is that the strings below are what would be used in a subfolder
// approach to data tidying. Ie, the New York data would be in a subfolder
// called 'NY'. For more info: https://github.com/GSA/sdg-indicators/issues/655#issuecomment-342678277
var state_ids = {
  'AL': '01',
  'AK': '02',
  'AZ': '04',
  'AR': '05',
  'CA': '06',
  'CO': '08',
  'CT': '09',
  'DE': '10',
  'DC': '11',
  'FL': '12',
  'GA': '13',
  'HI': '15',
  'ID': '16',
  'IL': '17',
  'IN': '18',
  'IA': '19',
  'KS': '20',
  'KY': '21',
  'LA': '22',
  'ME': '23',
  'MD': '24',
  'MA': '25',
  'MI': '26',
  'MN': '27',
  'MS': '28',
  'MO': '29',
  'MT': '30',
  'NE': '31',
  'NV': '32',
  'NH': '33',
  'NJ': '34',
  'NM': '35',
  'NY': '36',
  'NC': '37',
  'ND': '38',
  'OH': '39',
  'OK': '40',
  'OR': '41',
  'PA': '42',
  'RI': '44',
  'SC': '45',
  'SD': '46',
  'TN': '47',
  'TX': '48',
  'UT': '49',
  'VT': '50',
  'VA': '51',
  'WA': '53',
  'WV': '54',
  'WI': '55',
  'WY': '56',
  'AS': '60',
  'FM': '64',
  'GU': '66',
  'MH': '68',
  'MP': '69',
  'PW': '70',
  'PR': '72',
  'UM': '74',
  'VI': '78'
};
// Also flip the above object for reverse lookups later.
var state_abbreviations = {};
for(var key in state_ids) {
  state_abbreviations[state_ids[key]] = key;
}

// This hardcoded list of goal colors for d3's chromatic scale schemes.
var goal_schemes = {
  '1': d3.schemeReds,
  '2': d3.schemeOranges,
  '3': d3.schemeGreens,
  '4': d3.schemeReds,
  '5': d3.schemeReds,
  '6': d3.schemeBlues,
  '7': d3.schemeOranges,
  '8': d3.schemePurples,
  '9': d3.schemeOranges,
  '10': d3.schemePurples,
  '11': d3.schemeOranges,
  '12': d3.schemeOranges,
  '13': d3.schemeGreens,
  '14': d3.schemeBlues,
  '15': d3.schemeGreens,
  '16': d3.schemeBlues,
  '17': d3.schemeBlues
};
var goal = map_vars.indicator_id.split('-')[0];
var color_scheme = goal_schemes[goal];

// Load our data files and then continue.
d3.queue()
  .defer(d3.csv, map_vars.base_url + '/data/tidy/indicator_' + map_vars.indicator_id + '.csv')
  .defer(d3.json, 'https://d3js.org/us-10m.v1.json')
  .await(ready);

// This function hides the map and displays a message, for the cases where the
// data is not actually ready for subnational mapping.
// @TODO: Make this multilingual.
function abort() {
  $(container)
    .hide()
    .after('<h4>Subnational data is not yet available for this indicator.</h4>');
}

// This function only executed after indicator data and geo data has been loaded.
function ready(error, data, us) {
  if (error) throw error;

  // To get the aggregated data, we need the rows that have the correct year,
  // a value, but no other columns filled out. So first get the other columns.
  var otherColumns = [];
  var hasYear = false;
  var hasValue = false;
  var hasState = false;
  for (var column in data[0]) {
    if ('year' == column) {
      hasYear = true;
    }
    else if ('value' == column) {
      hasValue = true;
    }
    else if ('state' == column) {
      hasState = true;
    }
    else {
      otherColumns.push(column);
    }
  }

  // We can't continue without certain minimum columns.
  if (!hasYear || !hasValue || !hasState) {
    abort();
    return;
  }

  // Filter down the data.
  data = data.filter(function(row) {
    // We only care about rows with state.
    if (row.state == '') {
      return false;
    }
    // We only want aggregate data, so there should be no other columns present.
    for (var i in otherColumns) {
      if (row[otherColumns[i]] != '') {
        return false;
      }
    }
    return true;
  });

  // Make sure we still have data.
  if (!data.length) {
    abort();
    return;
  }

  // Get a sorted list of the years available.
  var years = d3.map(data, function(d) { return +d.year; }).keys().sort();

  // Show the year widget.
  $('#map-year').show();
  var $btnPrev = $('#map-previous').click(previousYear);
  var $btnNext = $('#map-next').click(nextYear);
  var $btnCurrent = $('#map-current');

  // Get the max and min values.
  var minValue = d3.min(data, function(d) { return +d.value; });
  var maxValue = d3.max(data, function(d) { return +d.value; });

  // A horizontal scale for the legend.
  var legendScale = d3.scaleLinear()
    .domain([minValue, maxValue])
    .rangeRound([600, 860]);

  // A threshold scale for the colors of the legend.
  var num_steps = 9;
  var step_size = (maxValue - minValue) / (num_steps - 1);
  var steps = d3.range(minValue, maxValue + step_size, step_size);
  var color = d3.scaleThreshold()
    .domain(steps)
    .range(color_scheme[num_steps]);

  // Start drawing the legend.
  var g = svg.append('g')
    .attr('transform', 'translate(0,40)');

  // Convert each "color step" into a colored rectangle.
  g.selectAll('rect')
    .data(color.range().map(function(d) {
      d = color.invertExtent(d);
      if (d[0] == null) d[0] = legendScale.domain()[0];
      if (d[1] == null) d[1] = legendScale.domain()[1];
      return d;
    }))
    .enter().append('rect')
      .attr('height', 8)
      .attr('x', function(d) { return legendScale(d[0]); })
      .attr('width', function(d) { return legendScale(d[1]) - legendScale(d[0]); })
      .attr('fill', function(d) { return color(d[0]); });

  // Add the legend text.
  g.append('text')
    .attr('class', 'caption')
    .attr('x', legendScale.range()[0])
    .attr('y', -6)
    .attr('fill', '#000')
    .attr('text-anchor', 'start')
    .attr('font-weight', 'bold')
    .text(map_vars.legend_text);

  // Add the tick marks.
  var tickValues = color.domain();
  g.call(d3.axisBottom(legendScale)
      .tickSize(13)
      .tickFormat(d3.format(".0f"))
      .tickValues(tickValues))
    .select('.domain')
      .remove();

  // Finally do the initial map rendering, starting with the most recent year.
  var currentYearIndex = years.length - 1;
  updateYear();

  // Switch to the previous year.
  function previousYear() {
    currentYearIndex -= 1;
    if (currentYearIndex < 0) {
      currentYearIndex = 0;
    }
    updateYear();
  }

  // Switch to the next year.
  function nextYear() {
    currentYearIndex += 1;
    if (currentYearIndex >= years.length) {
      currentYearIndex = years.length - 1;
    }
    updateYear();
  }

  // Function to update the current year.
  function updateYear() {
    $btnPrev.attr('disabled', currentYearIndex == 0);
    $btnNext.attr('disabled', currentYearIndex >= years.length - 1);
    $btnCurrent.html(years[currentYearIndex]);
    renderMap();
  }

  // Function to render the map.
  function renderMap() {

    var year = years[currentYearIndex];

    // Clear the previous map to start.
    svg.select('.states').remove();

    // Filter to this particular year.
    var data_by_year = data.filter(function(row) {
      if (row.year != year) {
        return false;
      }
      return true;
    });

    // Map the data according to the state's id code.
    var data_by_id = {};
    for (var row in data_by_year) {
      data_by_id[state_ids[data_by_year[row].state]] = data_by_year[row].value;
    }

    // Draw the map.
    svg.append('g')
        .attr('class', 'states')
      .selectAll('path')
      .data(topojson.feature(us, us.objects.states).features)
      .enter().append('path')
        .attr('class', 'state')
        .attr('fill', function(d) { return color(d.num = data_by_id[d.id]); })
        .attr('d', path)
        .attr('title', function(d) { return state_abbreviations[d.id] + ': ' + d.num; });

    tippy('svg .state', {
      size: 'large',
      performance: true,
      followCursor: true
    });
  }
}