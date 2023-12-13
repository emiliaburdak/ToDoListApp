function updateTime() {
    var dateTime = new Date();
    var date = dateTime.toLocaleDateString();
    var time = dateTime.toLocaleTimeString();

    document.getElementById('date-time').innerHTML = date + ' ' + time;
}

setInterval(updateTime, 1000);


function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.reload()
  });
}

function mark_update(noteId) {
  fetch("/mark_update", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((res) => {
    res.json().then((data) => {
      if (data.complete) {
        const checkbox = document.querySelector(`input[type='checkbox'][value='${noteId}']`);
        checkbox.checked = !checkbox.checked;
      }
      window.location.reload()
    });
  });
}

function mark_important(noteId){
    fetch("/mark_important", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId })
    }).then((res) => {
      res.json().then((data) => {
      if (data.important) {
        const btn = document.querySelector(`button[value='${noteId}']`);
        btn.classList.add('btn-danger');
        }
        window.location.reload()
      });
    });
  }

function editNote(noteId, currentNoteData) {
    const updatedNoteData = prompt("Edit your note:", currentNoteData);
    if (updatedNoteData != null && updatedNoteData != currentNoteData) {
        fetch('/edit-note', {
            method: 'POST',
            body: JSON.stringify({noteId: noteId, updatedNoteData: updatedNoteData}),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            location.reload();
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }
}

