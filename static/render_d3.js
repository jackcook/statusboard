var margin = {top: 2, right: 6, bottom: 30, left: 27},
  width = 600 - margin.left - margin.right,
  height = 100 - margin.top - margin.bottom;

var x = d3.time.scale()
  .range([0, width]);

var y = d3.scale.linear()
  .range([height, 0]);

var xAxis = d3.svg.axis()
  .scale(x)
  .ticks(5)
  .tickSize(0)
  .tickPadding(11)
  .orient("bottom");

var yAxis = d3.svg.axis()
  .scale(y)
  .ticks(3)
  .tickSize(0)
  .tickPadding(8)
  .orient("left");

var line = d3.svg.line()
  .x(function(d) { return x(d.timestamp); })
  .y(function(d) { return y(d.time); });

var svg = d3.select(".graph").append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var loadData = function(error, data) {
  if (error) throw error;

  var parseDate = d3.time.format("%Y-%m-%d %H:%M:%S").parse;

  data.forEach(function(d) {
    d.timestamp = parseDate(d.timestamp);
    d.time = +d.time;
  });

  x.domain(d3.extent(data, function(d) { return d.timestamp; }));
  y.domain(d3.extent(data, function(d) { return d.time; }));

  svg.selectAll("g").remove();
  svg.selectAll("path").remove();

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  svg.append("path")
      .datum(data)
      .attr("class", "line")
      .attr("d", line);

  var total = 0;
  for (var i = 0; i < data.length; i++) {
    total += data[i].time;
  }

  var mean = total / data.length;
  var user_mean = Math.round(mean);

  var value = document.getElementsByClassName("value")[0];
  value.innerHTML = user_mean + 'ms';
};

function clearSelected() {
  var dayButton = document.getElementById("day");
  var weekButton = document.getElementById("week");
  var monthButton = document.getElementById("month");

  dayButton.className = "";
  weekButton.className = "";
  monthButton.className = "";
}

document.addEventListener("click", function(e) {
  e = e || window.event;
  var target = e.target || e.srcElement;
  var controls = target.parentElement.parentElement.parentElement;
  if (controls.className == "controls") {
    var table = controls.parentElement.className;
    if (target.innerHTML == "Day") {
      loadDay(table);
    } else if (target.innerHTML == "Week") {
      loadWeek(table);
    } else if (target.innerHTML == "Month") {
      loadMonth(table);
    }
  }
});

function loadDay(table) {
  d3.csv("./data?q=day&t=" + table, loadData);

  clearSelected();

  var dayButton = document.getElementById("day");
  dayButton.className = "selected";
}

function loadWeek() {
  d3.csv("./data?q=week&t=" + table, loadData);

  clearSelected();

  var weekButton = document.getElementById("week");
  weekButton.className = "selected";
}

function loadMonth() {
  d3.csv("./data?q=month&t=" + table, loadData);

  clearSelected();

  var monthButton = document.getElementById("month");
  monthButton.className = "selected";
}
