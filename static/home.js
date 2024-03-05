// Get the elements by their ID

console.log('script accessed');

function showPopup() {
  // Show the pop-up window when the link is clicked
  var popupWindow = document.getElementById("popup-window");
    popupWindow.style.display = "block";
    console.log('show');
};

function hidePopup() {
  // Hide the pop-up window when the close button is clicked
  var popupWindow = document.getElementById("popup-window");
  popupWindow.style.display = "none";
  console.log('hide');
};