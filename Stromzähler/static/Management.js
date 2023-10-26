const info_screen = document.getElementById("info_content");
const meter_selection = document.getElementById("meter_selection");

const toastLive = document.getElementById('liveToast')

let url_prefix = "/service-worker"
let meter_prefix = "/meter"

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

const pull_mails = () => {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', url_prefix + '/transfer-mails/', true);
    xhr.send();
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if(xhr.status === 200) {
                let mails_arr = JSON.parse(this.responseText);
                document.getElementById("amount-new-mails").textContent = "" + mails_arr.length
                mails_arr.forEach(mail => {
                    let mail_elem = document.createElement('li');
                    mail_elem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
                    mail_elem.value = mail[0];
                    let since_elem = document.createElement("span");
                    since_elem.textContent = mail[1];
                    since_elem.classList.add("badge", "bg-primary");
                    mail_elem.appendChild(since_elem);
                    meter_selection.appendChild(mail_elem);
                })
            }else{
                console.log(xhr.responseText)
            }
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
    let uuid = meter_selection.options[ meter_selection.selectedIndex ].value

    let xhr = new XMLHttpRequest();
    xhr.open('POST', `${meter_prefix}/${uuid}/setup/`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    let reg_code = {"uuid": uuid, "code": 1234, "url": "http://127.0.0.1:5000/meter"}
    let body = JSON.stringify({
      uuid: uuid,
      registrationCode: JSON.stringify(reg_code)
    });
    xhr.send(body);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
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
    pull_mails()
}, 10000);