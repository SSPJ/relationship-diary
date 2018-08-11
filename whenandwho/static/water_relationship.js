// Relationship Diary, Seamus Johnston, 2018, GPLv3
let displayNoteConfirmation = function(pk) {
  let tr = document.getElementById(`rec${pk}`);
  let outputDiv = document.getElementById('toast');
  let name = tr.firstElementChild.firstElementChild.textContent.trim();
  let outStr = `Note saved to ${name}. <a href="javascript:void(0)" onclick="location.reload();">Refresh</a> page?`;
  outputDiv.innerHTML = outStr;
}

let uploadNote = function(event, pk) {
  let xhr = new XMLHttpRequest();
  let payload = document.getElementById(`collect-note-${pk}`).value;
  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  xhr.onload = function() {
    if (this.status >= 200 && this.status <= 300) {
        document.getElementById(`collect-note-tr-${pk}`).remove();
        displayNoteConfirmation(pk);
    } else {
      alert(this.status);
    }
  }
  xhr.onerror = function() {
    alert("oh no, a connection error :(");
  }
  xhr.open('post', `/api/v1/note/create/${pk}`, true);
  xhr.setRequestHeader("Content-type", "text/text");
  xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
  xhr.setRequestHeader("X-CSRFToken", token);
  xhr.send(payload);
}

let displayNoteArea = function(pk) {
  let tr = document.getElementById(`rec${pk}`);
  let newTr = document.createElement('tr');
  newTr.id = `collect-note-tr-${pk}`;
  let newTd = document.createElement('td');
  newTd.colSpan = "6";
  newTd.style.textAlign = "center";
  newTd.innerHTML = `<form><label for="collect-note-${pk}">Great job! Anything memorable?</label>` + 
    ` <a href="javascript:void(0)" onclick="uploadNote(event, ${pk})" title="Save Note">💾</a><br/>` +
    `<textarea class="textarea-note" id="collect-note-${pk}" name="collect-note" /></textarea>` +
    '</form>';
  newTr.appendChild(newTd);
  tr.parentNode.insertBefore(newTr, tr.nextSibling);
}

let water = function(event, pk) {
  let xhr = new XMLHttpRequest();
  xhr.onload = function() {
    if (this.status == 204) {
      displayNoteArea(pk);
    } else {
      alert(this.status);
    }
  }
  xhr.onerror = function() {
    alert("oh no, a connection error :(");
  }
  xhr.open('get',`/api/v1/water/${pk}`,true);
  xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
  xhr.send(null);
}