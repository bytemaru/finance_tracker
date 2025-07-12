import _ from 'lodash';
import * as d3 from 'd3';


const width = 600;
const height = 400;

const svg = d3.select("#treemap").append("svg").attr("width", width).attr("height", height);

let currentCategoryShown = null;

let startDate = "2024/01/01"
let endDate = "2026/01/01"


function formatDate(date) {
    return `${date.getFullYear()}/${String(date.getMonth() + 1).padStart(2,'0')}/${String(date.getDate()).padStart(2,'0')}`;
}

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
        console.log("clicked", event, d);
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


function showTransactions(categoryName) {
    d3.csv("/transactions_cleaned.csv").then((transactions) => {
    const details = d3.select("#details");
    details.html("");

    details.append("h3").text(`Transactions for ${categoryName}`);

    const filtered = transactions.filter(d => d.Category === categoryName && d.Date >= startDate && d.Date <= endDate);

    const table = details.append("table").style("border-collapse", "collapse");
    const header = table.append("tr");
    header.append("th").text("Date").style("border", "1px solid #ccc").style("padding", "4px");
    header.append("th").text("Payee").style("border", "1px solid #ccc").style("padding", "4px");
    header.append("th").text("Amount").style("border", "1px solid #ccc").style("padding", "4px");

    filtered.forEach(tran => {
        console.log(tran.Date);
        const row = table.append("tr");
        row.append("td").text(tran.Date).style("border", "1px solid #ccc").style("padding", "4px");
        row.append("td").text(tran.Payee).style("border", "1px solid #ccc").style("padding", "4px");
        row.append("td").text(parseFloat(tran.Amount).toFixed(2)).style("border", "1px solid #ccc").style("padding", "4px");
    });
})}


function drawTreemap(){
    d3.csv("/transactions_cleaned.csv").then(data => {

        const categoryTotals = d3.rollups(
            data.filter(d => parseFloat(d.Amount) < 0 & d.Date >= startDate & d.Date <= endDate),
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
            .size([width, height])
            .padding(2)(root);

        const svg = d3.select("#treemap").append("svg");

        // Initial draw
        render(root);

        d3.select("#applyFilter").on("click", () => {
            const start = new Date(document.getElementById("startDate").value);
            const end = new Date(document.getElementById("endDate").value);
            console.log("Start Date:", formatDate(start));
            console.log("End Date:", formatDate(end));

            updateTreemap(formatDate(start), formatDate(end));
        });

        function updateTreemap(start, end) {
            if (start < end) {

                svg.remove();

                startDate = start;
                endDate = end;

                drawTreemap();

            } else {
                alert("Start date cannot be after the end date. Please correct your selection.")
            }}


        return svg.node();

    });
}

drawTreemap();

