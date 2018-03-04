// This is a proof-of-concept for using tidy data format and d3.js to visualize
// subnational data on maps.

/**
 * A global function for rendering the SDG indicator map.
 *
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
 *   "geojson_d3_callback"
 *     A callback function used to feed the geojson data into the d3 rendering
 *   "region_ids"
 *     An object consisting of each subnational region value, keyed to that
 *     region's "id" property in the geojson.
 *   "region_labels"
 *     An object consisting of each subnational region value, keyed to that
 *     region's human-readable label.
 */
function sdg_indicator_map(config) {

  var svg = d3.select('#map-regions');
  var width = +svg.attr('width');
  var height = +svg.attr('height');
  var heightRatio = height / width;
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
    var years = d3.map(data, function(d) { return d[config.data_column_year]; }).keys().sort();

    // Set up the year widget.
    var $btnPrev = $('#map-previous').click(previousYear);
    var $btnNext = $('#map-next').click(nextYear);
    var $btnCurrent = $('#map-current');

    // Get the max and min values.
    var getDataValue = function(d) {
      return +d[config.data_column_value];
    };
    var minValue = d3.min(data, getDataValue);
    var maxValue = d3.max(data, getDataValue);
    var threeDeviations = d3.deviation(data, getDataValue) * 3;
    var mean = d3.mean(data, getDataValue);

    // To prevent non-useful choropleth maps where one extreme outlier makes
    // all the other regions appear uniform, make sure that the minValue and
    // maxValue are not outside of 3 standard definitions from the mean. This
    // causes the legend to start and end at the less extreme values, and all
    // regions with extreme values will get the first or last color.
    if (minValue < mean - threeDeviations) {
      minValue = mean - threeDeviations;
    }
    if (maxValue > mean + threeDeviations) {
      maxValue = mean + threeDeviations;
    }

    // A horizontal scale for the legend.
    var legendScale = d3.scaleLinear()
      .domain([minValue, maxValue])
      .rangeRound([0, 260]);

    // A threshold scale for the colors of the legend.
    var num_steps = 9;
    var step_size = (maxValue - minValue) / (num_steps - 1);
    var steps = d3.range(minValue, maxValue + step_size, step_size);
    var color = d3.scaleThreshold()
      .domain(steps)
      .range(color_scheme[num_steps]);

    // Start drawing the legend.
    var legend = d3.select('#map-colors');
    var g = legend.append('g')
      .attr('transform', 'translate(10, 0)');

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
    $('#map-caption').html(config.legend_text);

    // Add the tick marks.
    var tickValues = color.domain();
    g.call(d3.axisBottom(legendScale)
        .tickSize(13)
        .tickFormat(d3.format(".0f"))
        .tickValues(tickValues))
      .select('.domain')
        .remove();

    // Make the map responsive to screen width changes.
    svg.attr('width', '100%');
    d3.select(window)
      .on('resize', resizeMap);

    // Finally do the initial map rendering, starting with the most recent year.
    var currentYearIndex = years.length - 1;
    updateYear();

    /**************** Helper functions *************************/

    /**
     * This function hides the map and displays a message, for the cases where
     * the data is not actually ready for subnational mapping.
     */
    function abort() {
      $('#map-container *').hide();
      $('#map-abort').show();
    }

    /**
     * Switch the map to the previous year.
     */
    function previousYear() {
      currentYearIndex -= 1;
      if (currentYearIndex < 0) {
        currentYearIndex = 0;
      }
      updateYear();
    }

    /**
     * Switch the map to the next year.
     */
    function nextYear() {
      currentYearIndex += 1;
      if (currentYearIndex >= years.length) {
        currentYearIndex = years.length - 1;
      }
      updateYear();
    }

    /**
     * Update the map according to the last specified year.
     */
    function updateYear() {
      $btnPrev.attr('disabled', currentYearIndex == 0);
      $btnNext.attr('disabled', currentYearIndex >= years.length - 1);
      $btnCurrent.html(years[currentYearIndex]);
      renderMap();
    }

    /**
     * Callback for whenever the screen is resized.
     */
    function resizeMap() {

      var parentWidth = $('#map-container').width();
      // At load time, parentWidth is 0. In that case, we have to use the SVG's
      // width, or the window's width if smaller.
      if (!parentWidth) {
        parentWidth = width;
        if (parentWidth > $(window).width()) {
          parentWidth = $(window).width();
        }
      }

      // Rescale the contents of the map SVG, making sure not to go bigger than
      // the original.
      var scale = parentWidth / width;
      if (scale > 1) {
        scale = 1;
      }
      d3.selectAll('#map-regions .regions').attr('transform', 'scale(' + scale + ')');

      // Give the svg a new height.
      $('#map-regions')
        .height(parentWidth * heightRatio);
	  }

    /**
     * Helper function to render the map.
     */
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
        .data(config.geojson_d3_callback(geojson))
        .enter().append('path')
          .attr('class', 'region')
          .attr('fill', function(d) { return color(d.num = data_by_id[d.id]); })
          .attr('d', path)
          .attr('title', function(d) { return region_labels[d.id] + ': ' + d.num; });

      // Enhance the tooltips using the Tippy library.
      tippy('#map-regions .region', {
        size: 'large',
        performance: true,
        followCursor: true
      });

      // Resize the map if needed.
      resizeMap();
    }
  }
}