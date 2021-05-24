 let submit = () => {
    let ROWS=Number(document.getElementById('rows').value)
    let COLS=Number(document.getElementById('cols').value)
    let NOISE=Number(document.getElementById('noise').value)
    let OCEAN=Number(document.getElementById('ocean').checked)
    let HEXAGON_FILE=document.getElementById('hex').value
    let COLORED_W_OCEAN_FILE=document.getElementById('map').value
    let WKT_FILE=document.getElementById('wkt').value

    let DISTRIBUTION = [
        Number(document.getElementById('grassland').value),
        Number(document.getElementById('dessert').value),
        Number(document.getElementById('water').value),
        0.0,
        Number(document.getElementById('mountain').value),
        Number(document.getElementById('forest').value)
    ]

    let sum=0.0
    DISTRIBUTION.forEach(el => {
        sum = sum + el
    })
    if(sum != 1) DISTRIBUTION = null

    toSubmit = {
        'ROWS': ROWS,
        'COLS': COLS,
        'NOISE': NOISE,
        'OCEAN': OCEAN,
        'HEXAGON_FILE': HEXAGON_FILE,
        'COLORED_W_OCEAN_FILE': COLORED_W_OCEAN_FILE,
        'WKT_FILE': WKT_FILE,
        'DISTRIBUTION': DISTRIBUTION
    }
    console.log("submit clicked", toSubmit);
    $.ajaxSetup({
        headers: {
            "accept": "application/json",
            "Access-Control-Allow-Origin":"*"
        },
        crossDomain: true,
        dataType: 'application/json'
     });
    $.post("http://localhost:5000/setParams", toSubmit, (data, status) => {
        console.log(data)
        console.log(status)
        }
    )
}

let generate = () => {
    $.post("http://localhost:5000/generate", (data, status) => {
        console.log(data)
        console.log(status)
        location.reload()
        }
    )
}