const monitoringId = 'monitoring';
const radius = 3;
var svg;
var xScale;
var yScale;
var colors = d3.scaleSequential().domain([0,20])
                .interpolator(d3.interpolateViridis);

function startMonitoring() {
  wsocket.permanentSubscribe('push_position', push_position, monitoringId);
  wsocket.promiseSubscribe('get_size').then(
    result => init(result),
    error  => console.log(error)
  );
  wsocket.sendRequest('get_size', {});
}

function stopMonitoring() {
  wsocket.unsubscribe(monitoringId);
  d3.select("#monitoring").selectAll('div').remove();
}

function clearSVG() {
  d3.selectAll("circle").remove();
}

function push_position(data) {
  x = data['position'][0];
  y = data['position'][1];
  var circle = svg.append('circle')
    .datum({'x' : x, 'y' : y, 't' : data['time'], 'id' : data['security_id']})
    .attr('cx', xScale(x))
    .attr('cy', yScale(y))
    .attr('r', radius)
    .attr('fill', colors(data['security_id'] % 20))
    .on("mouseover", handleMouseOver)
    .on("mouseout", handleMouseOut);
}

function init(data) {
  max_x = data.width;
  max_y = data.height;
  svg = d3.select("#monitoring")
          .append("div")
          .classed("svg-container", true) //container class to make it responsive
          .append("svg")
          //responsive SVG needs these 2 attributes and no width and height attr
          .attr("preserveAspectRatio", "xMinYMin meet")
          .attr("viewBox", "0 0 256 256")
          //class to make it responsive
          .classed("svg-content-responsive", true)
          .append("g")
          .attr("transform", "translate(20, 10)")


  xScale = d3.scaleLinear()
              .domain([0, max_x]) // input
              .range([0, 230]); // output

  yScale = d3.scaleLinear()
              .domain([0, max_y]) // input
              .range([230, 0]); // output

  svg.append("g")
          .attr("class", "x-axis")
          .attr("transform", "translate(0, 230)")
          .call(d3.axisBottom(xScale));

  svg.append("g")
          .attr("class", "y-axis")
          .call(d3.axisLeft(yScale));
}


function handleMouseOver(d, i) {
  d3.select(this)
    .attr('fill', "orange")
    .attr('r', radius * 2);
  svg.append("text")
     .attr('class', 'infoLabel')
     .attr('id', "t" + i)
     .attr('x', function() { return xScale(d.x) - 30; })
     .attr('y', function() { return yScale(d.y) - 15; })
     .text(function() {
       return `Security ${d.id}`;  // Value of the text
      });
   svg.append("text")
      .attr('class', 'infoLabel')
      .attr('id', "td" + i)
      .attr('x', function() { return xScale(0); })
      .attr('y', function() { return 0; })
      .text(function() {
          return `Security ${d.id} visit (${d.x.toFixed(1)}, ${d.y.toFixed(1)}) at ${d.t}`;
       });
}

function handleMouseOut(d, i) {
  d3.select(this)
    .attr('fill', colors(d.id  % 20))
    .attr('r', radius);
  d3.select("#t" + i).remove();
  d3.select("#td" + i).remove();
}
