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
// called 'new-york'. For more info: https://github.com/GSA/sdg-indicators/issues/655#issuecomment-342678277
var state_ids = {
  'alabama': '01',
  'alaska': '02',
  'arizona': '04',
  'arkansas': '05',
  'california': '06',
  'colorado': '08',
  'connecticut': '09',
  'delaware': '10',
  'district-of-columbia': '11',
  'florida': '12',
  'georgia': '13',
  'hawaii': '15',
  'idaho': '16',
  'illinois': '17',
  'indiana': '18',
  'iowa': '19',
  'kansas': '20',
  'kentucky': '21',
  'louisiana': '22',
  'maine': '23',
  'maryland': '24',
  'massachusetts': '25',
  'michigan': '26',
  'minnesota': '27',
  'mississippi': '28',
  'missouri': '29',
  'montana': '30',
  'nebraska': '31',
  'nevada': '32',
  'new-hampshire': '33',
  'new-jersey': '34',
  'new-mexico': '35',
  'new-york': '36',
  'north-carolina': '37',
  'north-dakota': '38',
  'ohio': '39',
  'oklahoma': '40',
  'oregon': '41',
  'pennsylvania': '42',
  'rhode-island': '44',
  'south-carolina': '45',
  'south-dakota': '46',
  'tennessee': '47',
  'texas': '48',
  'utah': '49',
  'vermont': '50',
  'virginia': '51',
  'washington': '53',
  'west-virginia': '54',
  'wisconsin': '55',
  'wyoming': '56',
  'america-samoa': '60',
  'federated-states-of-micronesia': '64',
  'guam': '66',
  'marshall-islands': '68',
  'northern-mariana-islands': '69',
  'palau': '70',
  'puerto-rico': '72',
  'us-minor-outlying-islands': '74',
  'us-virgin-islands': '78'
};

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
  .defer(d3.csv, map_vars.base_url + '/data/indicator_' + map_vars.indicator_id + '.csv')
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

  // A future improvement would be to implement disaggregation filtering
  // on these maps, but for now, we are just doing a hardcoded visualization
  // of the aggregated data for the most recent year, 2016. A necessary
  // improvement would be some sort of slider widget for changing the year.
  var year = '2016';

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
    // Ensure the correct year.
    if (row.year != year) {
      return false;
    }
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

  // Get the max and min values.
  var min = d3.min(data, function(d) { return +d.value; });
  var max = d3.max(data, function(d) { return +d.value; });

  // Map the data according to the state's id code.
  data_by_id = {};
  for (var row in data) {
    data_by_id[state_ids[data[row].state]] = data[row].value;
  }

  // A horizontal scale for the legend.
  var x = d3.scaleLinear()
    .domain([min, max])
    .rangeRound([600, 860]);

  // A threshold scale for the colors of the legend.
  var num_steps = 9;
  var step_size = (max - min) / (num_steps - 1);
  var steps = d3.range(min, max + step_size, step_size);
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
      if (d[0] == null) d[0] = x.domain()[0];
      if (d[1] == null) d[1] = x.domain()[1];
      return d;
    }))
    .enter().append('rect')
      .attr('height', 8)
      .attr('x', function(d) { return x(d[0]); })
      .attr('width', function(d) { return x(d[1]) - x(d[0]); })
      .attr('fill', function(d) { return color(d[0]); });

  // Add the legend text.
  g.append('text')
    .attr('class', 'caption')
    .attr('x', x.range()[0])
    .attr('y', -6)
    .attr('fill', '#000')
    .attr('text-anchor', 'start')
    .attr('font-weight', 'bold')
    .text(map_vars.legend_text);

  // Add the tick marks.
  g.call(d3.axisBottom(x)
      .tickSize(13)
      .tickFormat(d3.format(".0f"))
      .tickValues(color.domain()))
    .select('.domain')
      .remove();

  // Finally draw the map itself.
  svg.append('g')
      .attr('class', 'states')
    .selectAll('path')
    .data(topojson.feature(us, us.objects.states).features)
    .enter().append('path')
      .attr('fill', function(d) { return color(d.num = data_by_id[d.id]); })
      .attr('d', path)
    .append('title')
      .text(function(d) { return d.num; });
}