import _ from 'lodash';
import * as d3 from 'd3';



d3.csv("/transactions_cleaned.csv").then(data => {

    const width = 600;
    const height = 400;

    let currentCategoryShown = null;


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

    const svg = d3.select("#treemap").append("svg")
        .attr("width", width)
        .attr("height", height);

    let currentRoot = root;

    function render(node) {
        svg.selectAll("*").remove();

        const nodes = node.leaves();
        console.log("Rendering nodes:", nodes);

        const g = svg.selectAll("g")
            .data(nodes)
            .enter()
            .append("g")
            .attr("transform", d => `translate(${d.x0},${d.y0})`);

        g.append("rect")
            .attr("width", d => d.x1 - d.x0)
            .attr("height", d => d.y1 - d.y0)
            .attr("fill", d => d3.interpolateSpectral(Math.random()));

        g.append("text")
            .attr("x", 4)
            .attr("y", 14)
            .style("fill", "#fff")
            .style("font-size", "10px")
            .text(d => `${d.data.name}: $${d.value.toFixed(2)}`);

        g.on("click", (event, d) => {
            if (currentCategoryShown === d.data.name) {
                // Same category clicked again, toggle OFF
                d3.select("#details").html("");
                currentCategoryShown = null;
            } else {
                // Show transactions
                showTransactions(d.data.name);
                currentCategoryShown = d.data.name;
            }
        })

    }


// Initial draw
    render(root);

    function showTransactions(categoryName) {
        const details = d3.select("#details");
        details.html(""); // очищаем div

        details.append("h3").text(`Transactions for ${categoryName}`);

        const filtered = data.filter(d => d.Category === categoryName);

        const table = details.append("table").style("border-collapse", "collapse");
        const header = table.append("tr");
        header.append("th").text("Date").style("border", "1px solid #ccc").style("padding", "4px");
        header.append("th").text("Payee").style("border", "1px solid #ccc").style("padding", "4px");
        header.append("th").text("Amount").style("border", "1px solid #ccc").style("padding", "4px");

        filtered.forEach(tran => {
            const row = table.append("tr");
            row.append("td").text(tran.Date).style("border", "1px solid #ccc").style("padding", "4px");
            row.append("td").text(tran.Payee).style("border", "1px solid #ccc").style("padding", "4px");
            row.append("td").text(parseFloat(tran.Amount).toFixed(2)).style("border", "1px solid #ccc").style("padding", "4px");
        });
    }

    return svg.node();

});

function component() {
    const element = document.createElement('div');

    element.innerHTML = _.join(['Hello', 'webpack'], ' ');

    return element;
}

document.body.appendChild(component());
