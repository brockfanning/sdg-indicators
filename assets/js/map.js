// This is a proof-of-concept for using tidy data format and d3.js to visualize
// subnational data on maps.

/**
 * A global function for rendering the SDG indicator map.
 *
 * @param String container
 *   The CSS selector for the container of the map.
 * @param Object config
 *   An object containing all required configuration options. These consist of:
 *   "indicator_id"
 *     The id of the indicator, eg: 8-1-1
 *   "data_path"
 *     A web-accessible path to the CSV data file
 *   "data_column_year"
 *     The column header in the CSV that represents the year
 *   "data_column_value"
 *     The column header in the CSV that represents the value
 *   "data_column_region"
 *     The column header in the CSV that represents the subnational region
 *   "geojson_path"
 *     A web-accessible path to the geojson file
 *   "geojson_d3_data"
 *     A callback function used to feed the geojson data into the d3 rendering
 *   "region_ids"
 *     An object consisting of each subnational region value, keyed to that
 *     region's "id" property in the geojson.
 *   "region_labels"
 *     An object consisting of each subnational region value, keyed to that
 *     region's human-readable label.
 *   "legend_start"
 *     The number of pixels at which the legend starts
 *   "legend_end"
 *     The number of pixels at which the legend ends
 *   "legend_text"
 *     The text to display above the legend
 *   "abort_text"
 *     The message to display if the data does not support subnational display
 *   "button_text_previous"
 *     The text for the "Previous" button
 *   "button_text_next"
 *     The text for the "Next" button
 */
function sdg_indicator_map(container, config) {

  var svg = d3.select(container);
  var width = +svg.attr('width');
  var height = +svg.attr('height');
  var path = d3.geoPath();

  // This hardcoded list of goal colors for d3's chromatic scale schemes.
  // @TODO: Replace these with custom color schemes to match SDG branding.
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
  var goal = config.indicator_id.split('-')[0];
  var color_scheme = goal_schemes[goal];

  // Load our data files and then continue.
  d3.queue()
    .defer(d3.csv, config.data_path)
    .defer(d3.json, config.geojson_path)
    .await(ready);

  // This function hides the map and displays a message, for the cases where the
  // data is not actually ready for subnational mapping.
  function abort() {
    $(container)
      .hide()
      .after('<h4>' + config.abort_text + '</h4>');
  }

  // This function only executed after indicator data and geo data has been loaded.
  function ready(error, data, geojson) {
    if (error) throw error;

    // To get the aggregated data, we need the rows that have the correct year,
    // a value, but no other columns filled out. So first get the other columns.
    var otherColumns = [];
    var hasYear = false;
    var hasValue = false;
    var hasRegion = false;
    for (var column in data[0]) {
      if (config.data_column_year == column) {
        hasYear = true;
      }
      else if (config.data_column_value == column) {
        hasValue = true;
      }
      else if (config.data_column_region == column) {
        hasRegion = true;
      }
      else {
        otherColumns.push(column);
      }
    }

    // We can't continue without certain minimum columns.
    if (!hasYear || !hasValue || !hasRegion) {
      abort();
      return;
    }

    // Filter down the data.
    data = data.filter(function(row) {
      // We only care about rows with regions.
      if (row[config.data_column_region] == '') {
        return false;
      }
      // We only want aggregate data, so there should be no other columns present.
      // @TODO: How can we allow for disaggregated maps?
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

    // For the tooltips later, we need an id-to-label object.
    var region_labels = {};
    for (var key in config.region_ids) {
      region_labels[config.region_ids[key]] = config.region_labels[key];
    }

    // Get a sorted list of the years available.
    var years = d3.map(data, function(d) { return +d[config.data_column_year]; }).keys().sort();

    // Show the year widget.
    $('#map-year').show();
    var $btnPrev = $('#map-previous').click(previousYear);
    var $btnNext = $('#map-next').click(nextYear);
    var $btnCurrent = $('#map-current');

    // Get the max and min values.
    var minValue = d3.min(data, function(d) { return +d[config.data_column_value]; });
    var maxValue = d3.max(data, function(d) { return +d[config.data_column_value]; });

    // A horizontal scale for the legend.
    var legendScale = d3.scaleLinear()
      .domain([minValue, maxValue])
      .rangeRound([config.legend_start, config.legend_end]);

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
      .text(config.legend_text);

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
      svg.select('.regions').remove();

      // Filter to this particular year.
      var data_by_year = data.filter(function(row) {
        if (row[config.data_column_year] != year) {
          return false;
        }
        return true;
      });

      // Map the data according to the region's id code.
      var data_by_id = {};
      for (var row in data_by_year) {
        var region_key = data_by_year[row][config.data_column_region];
        var region_value = data_by_year[row][config.data_column_value];
        var region_id = config.region_ids[region_key];
        data_by_id[region_id] = region_value;
      }

      // Draw the map.
      svg.append('g')
          .attr('class', 'regions')
        .selectAll('path')
        .data(config.geojson_d3_data(geojson))
        .enter().append('path')
          .attr('class', 'region')
          .attr('fill', function(d) { return color(d.num = data_by_id[d.id]); })
          .attr('d', path)
          .attr('title', function(d) { return region_labels[d.id] + ': ' + d.num; });

      tippy('svg .region', {
        size: 'large',
        performance: true,
        followCursor: true
      });
    }
  }
}