const searchButton = document.getElementById('search-btn');
const whereInput = document.getElementById('where-input');
const message = document.getElementById('message');
const favoriteButtons = document.querySelectorAll('.fav-btn');

searchButton.addEventListener('click', () => {
  const destination = whereInput.value.trim() || 'your destination';
  message.textContent = `Showing homes in ${destination}.`;
});

favoriteButtons.forEach((button) => {
  button.addEventListener('click', () => {
    button.classList.toggle('active');
    button.textContent = button.classList.contains('active') ? '❤' : '♡';
  });
});
