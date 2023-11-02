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
                if(mails_arr.length <= 0) {
                    return
                }
                document.getElementById("amount-new-mails").textContent = "" + mails_arr.length
                let mailWrapper = document.getElementById("mail-list")
                mails_arr.forEach(mail => {
                    let mail_elem = document.createElement('li');
                    mail_elem.classList.add("list-group-item", "d-flex", "justify-content-between", "align-items-center");
                    mail_elem.textContent = mail[0];
                    let d = new Date(0); // The 0 there is the key, which sets the date to the epoch
                    d.setUTCSeconds(mail[1]);
                    let options = {month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: 'false' }
                    let since_elem = document.createElement("span");
                    since_elem.textContent = d.toLocaleTimeString("de-DE");
                    since_elem.classList.add("badge", "bg-primary");
                    mail_elem.appendChild(since_elem);
                    mailWrapper.appendChild(mail_elem);
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
    if(meter_selection.selectedIndex == -1) {
        info_screen.textContent += "No meter selected\r\n";
        hideOverlay();
        return;
    }
    let uuid = meter_selection.options[ meter_selection.selectedIndex ].value;
    let registerCode = document.getElementById("action-value").value;

    hideOverlay();
    let xhr = new XMLHttpRequest();
    xhr.open('POST', `${meter_prefix}/${uuid}/setup/`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    let reg_code = {"uuid": uuid, "code": registerCode, "url": "http://127.0.0.1:5000/meter"}
    let body = JSON.stringify({
      uuid: uuid,
      registrationCode: JSON.stringify(reg_code)
    });
    xhr.send(body);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            info_screen.textContent += xhr.responseText + "\r\n";
        }
    }
}

let set_meter = () => {
    if(meter_selection.selectedIndex == -1) {
        info_screen.textContent += "No meter selected\r\n";
        hideOverlay();
        return;
    }
    let uuid = meter_selection.options[ meter_selection.selectedIndex ].value;
    let amount = document.getElementById("action-value").value;

    hideOverlay();
    let xhr = new XMLHttpRequest();
    xhr.open('POST', `${meter_prefix}/${uuid}/set/`, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    let body = JSON.stringify({
      amount: amount
    });
    xhr.send(body);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            info_screen.textContent += xhr.responseText + "\r\n";
        }
    }
}

let showOverlay = (action, placeholderText) => {
    document.getElementById("action-value").placeholder = placeholderText;
    document.getElementById("trigger-action").onclick = action;
    document.getElementById("overlay").style.display = "flex";
}

let hideOverlay = () => {
    document.getElementById("overlay").style.display = "None";
    document.getElementById("trigger-action").onclick = null;
    document.getElementById("action-value").placeholder = "";
    document.getElementById("action-value").value = "";
}

setInterval(function (){
    pull_meter_list()
    pull_mails()
}, 10000);

document.getElementById("mail-open-button").addEventListener("click", (e) => {
    document.getElementById("amount-new-mails").textContent = "" + 0
});