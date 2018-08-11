// Relationship Diary, Seamus Johnston, 2018, GPLv3
let displayJSON = function(forms_html) {
  let outputDiv = document.getElementById('import-output-div');
  outputDiv.innerHTML = forms_html;
  // debugging code
  // for (let i = 0, length = vCards.length; i < length; i++) {
  //   let outputText = document.createTextNode(JSON.stringify(vCards[i], null, 2));
  //   outputDiv.appendChild(outputText);
  // }
}

let uploadJSON = function() {
  let xhr = new XMLHttpRequest();
  let payload = JSON.stringify(vCards);
  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  xhr.onload = function() {
    if (this.status == 204) {
      location.reload(true);
    } else if (this.status >=200 && this.status < 300) {
      displayJSON(this.response);
    } else {
      alert(this.status);
    }
  }
  xhr.onerror = function() {
    alert("a connection error :(");
  };
  xhr.open('post','/api/v1/populate', true);
  xhr.setRequestHeader("Content-type", "application/json");
  xhr.setRequestHeader("Content-length", payload.length);
  xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
  xhr.setRequestHeader("X-CSRFToken", token);
  xhr.setRequestHeader("Connection", "close");
  xhr.send(payload);
}

// Listens on a FileReader()'s onload and converts a .cvf into a JSON representation
let vCardSplitter = function(event) {
  let fileText = event.target.result;
  let vCardsText = fileText.split(/END:VCARD[\r\n]+BEGIN:VCARD/);
  vCardsText[0] = vCardsText[0].replace("BEGIN:VCARD\r\n","");
  vCardsText[vCardsText.length-1] = vCardsText[vCardsText.length-1].replace("END:VCARD","");
  //console.log(vCardsText);

  for (let i = 0, length = vCardsText.length; i < length; i++) {
    parseString(vCardsText[i], function(err, json) {
      if(err) return console.log(err);
      vCards.push(json);
    });
    //console.log(vCards);
  }
  if (vCardsText.length >= 20) {
    document.getElementById('import-output-div').innerHTML = "<b>Processing. Hang tight.</b>";
  }
  uploadJSON();
};

let getVCardFile = function(event) {
  let reader = new FileReader();
  reader.onload = vCardSplitter;

  reader.readAsText(event.target.files[0]);
};

let importContactsForm = document.getElementById('import-contacts-file-selector');
importContactsForm.onchange = getVCardFile;
let vCards = [];
