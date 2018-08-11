// Relationship Diary, Seamus Johnston, 2018, GPLv3
let changeDate = function(event) {
  let next_contact_date = document.getElementById('id_next_contact_date');
  let date = new Date();
  switch (event.target.value) {
    case "0": date.setFullYear(9999,11,30);       break;
    case "1": date.setDate(date.getDate() + 356); break;
    case "2": date.setDate(date.getDate() + 178); break;
    case "3": date.setDate(date.getDate() + 89);  break;
    case "4": date.setDate(date.getDate() + 30);  break;
    case "5": date.setDate(date.getDate() + 15);  break;
    case "6": date.setDate(date.getDate() + 7);   break;
    case "7": date.setDate(date.getDate() + 1);   break;
  }
  next_contact_date.value = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}
document.getElementById('id_frequency').onchange = changeDate;