var mainmap = L.map('mainmap').setView([47, 2.5], 6);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mainmap);

//var geomrn = JSON.parse('{{ geomrn|safe }}')
L.geoJSON('http://127.0.0.1:5000/geojson-features').addTo(mainmap);
//axios.get('http://127.0.0.1:5000/geojson-features')
//            .then(response => {
//                console.log(response.data)
//                L.geoJSON(response.data, {}).addTo(mainmap);//

            //})
