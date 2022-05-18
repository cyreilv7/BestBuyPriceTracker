let checkedBoxes = document.querySelectorAll('.checked');
let uncheckedBoxes = document.querySelectorAll('.unchecked');
checkedBoxes.forEach(box => box.checked = true);
uncheckedBoxes.forEach(box => box.checked = false);

let reminder = document.querySelector('.reminder-checkbox');
let input = document.querySelector('.reminder-freq');
reminder.addEventListener("click", (e) => {
    if (e.target.checked) {
        input.disabled = false;
    } else { 
        input.disabled = true;
        input.value = "";
    }
});