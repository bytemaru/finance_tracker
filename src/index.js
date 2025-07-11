import _ from 'lodash';
import * as d3 from 'd3';



d3.csv("/transactions_cleaned.csv").then(data => {

    const width = 928;
    const height = 924;

    function tile(node, x0, y0, x1, y1) {
        d3.treemapBinary(node, 0, 0, width, height);
        for (const child of node.children) {
            child.x0 = x0 + child.x0 / width * (x1 - x0);
            child.x1 = x0 + child.x1 / width * (x1 - x0);
            child.y0 = y0 + child.y0 / height * (y1 - y0);
            child.y1 = y0 + child.y1 / height * (y1 - y0);
        }}

    const categoryTotals = d3.rollups(
        data.filter(d => parseFloat(d.Amount) < 0),
        v => d3.sum(v, d => -parseFloat(d.Amount)),
        d => d.Category
    );

    console.log("IS ARRAY?", Array.isArray(categoryTotals));

    const hierarchy = {
        name: "root",
        children: categoryTotals.map(([name, value]) => ({
            name,
            value
        }))
    };

    console.log(hierarchy);

    const root = d3.hierarchy(hierarchy)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);

    d3.treemap()
        .size([600, 400])
        .padding(2)(root);
    

    const svg = d3.select("body")
        .append("svg")
        .attr("width", 600)
        .attr("height", 400);

    const nodes = svg.selectAll("g")
        .data(root.leaves())
        .enter()
        .append("g")
        .attr("transform", d => `translate(${d.x0},${d.y0})`);

    nodes.append("rect")
        .attr("width", d => d.x1 - d.x0)
        .attr("height", d => d.y1 - d.y0)
        .attr("fill", d => d3.interpolateSpectral(Math.random()));

    nodes.append("text")
        .attr("x", 3)
        .attr("y", 14)
        .text(d => `${d.data.name}: $${d.value.toFixed(2)}`);
});


function component() {
    const element = document.createElement('div');

    element.innerHTML = _.join(['Hello', 'webpack'], ' ');

    return element;
}

document.body.appendChild(component());
