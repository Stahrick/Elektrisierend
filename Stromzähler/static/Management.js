const info_screen = document.getElementById("info_content");
const meter_selection = document.getElementById("meter_selection");

let url_prefix = "/service-worker"

const pull_meter_list = () => {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', url_prefix + '/list/', true);
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let device_arr = JSON.parse(this.responseText);
            meter_selection.options.length = 0;
            device_arr.forEach(device => {
                let opt = document.createElement('option');
                opt.value = device;
                opt.innerHTML = device;
                meter_selection.appendChild(opt);
            })
        }
    }
}

let create_meter = () => {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', url_prefix + '/create/', true);
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            info_screen.textContent += xhr.responseText + "\r\n";
            pull_meter_list()
        }
    }
}

let setup_meter = () => {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', url_prefix + '/setup/', true);
    xhr.setRequestHeader("Content-Type", "application/json");
    let body = JSON.stringify({
      uuid: meter_selection.options[ meter_selection.selectedIndex ].value,
      registrationCode: 10
    });
    xhr.send(body);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            if(xhr.status === 200) {
                info_screen.textContent += xhr.responseText + "\r\n";
            }else{
                info_screen.textContent += xhr.responseText + "\r\n";
            }
        }

    }
}

setInterval(function (){
    pull_meter_list()
}, 10000);