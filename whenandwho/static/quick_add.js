// Relationship Diary, Seamus Johnston, 2018, GPLv3
let displayContactLink = function(contactLink) {
  let outputDiv = document.getElementById('toast');
  outputDiv.innerHTML = contactLink;
}

let uploadContactString = function() {
  let xhr = new XMLHttpRequest();
  let payload = document.getElementById('quick-add').value
  let token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
  xhr.onload = function() {
    if (this.status >=200 && this.status < 300) {
      displayContactLink(this.response);
    } else {
      alert(this.status);
    }
  }
  xhr.onerror = function() {
    alert("a connection error :(");
  };
  xhr.open('post','/api/v1/quick_add', true);
  xhr.setRequestHeader("Content-type", "text/text");
  xhr.setRequestHeader("Content-length", payload.length);
  xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
  xhr.setRequestHeader("X-CSRFToken", token);
  xhr.setRequestHeader("Connection", "close");
  xhr.send(payload);
  return false;
}

let quickContactButton = document.getElementById('quick-add-submit');
quickContactButton.onclick = uploadContactString;