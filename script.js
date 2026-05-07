const searchButton = document.getElementById('search-btn');
const whereInput = document.getElementById('where-input');
const message = document.getElementById('message');

const cardsContainer = document.getElementById('cards');
const bookingForm = document.getElementById('booking-form');

const listingDetail = document.getElementById('listing-detail');
const detailImage = document.getElementById('detail-image');
const detailLocation = document.getElementById('detail-location');
const detailTitle = document.getElementById('detail-title');
const detailMeta = document.getElementById('detail-meta');
const detailPrice = document.getElementById('detail-price');

const userNameInput = document.getElementById('user-name');
const userEmailInput = document.getElementById('user-email');
const checkInInput = document.getElementById('book-check-in');
const checkOutInput = document.getElementById('book-check-out');
const bookingGuestsInput = document.getElementById('book-guests');

const state = {
  stays: [],
  selectedStayId: '',
};

const renderStays = (stays) => {
  cardsContainer.innerHTML = '';

  stays.forEach((stay) => {
    const card = document.createElement('article');
    card.className = 'card';

    card.innerHTML = `
      <button class="fav-btn" aria-label="Save listing">♡</button>
      <div class="card-image ${stay.image_class}"></div>
      <div class="card-body">
        <p class="location">${stay.location}</p>
        <h3>${stay.title}</h3>
        <p class="meta">${stay.guests} guests · ${stay.bedrooms} bedrooms · ${stay.beds} beds</p>
        <p class="price">$${stay.price_per_night} night</p>
        <button class="book-btn" data-stay-id="${stay.stay_id}" type="button">View listing</button>
      </div>
    `;

    cardsContainer.appendChild(card);
  });
};

const selectStay = (stayId) => {
  const stay = state.stays.find((item) => item.stay_id === stayId);
  if (!stay) {
    return;
  }

  state.selectedStayId = stay.stay_id;
  detailImage.className = `listing-image ${stay.image_class}`;
  detailLocation.textContent = stay.location;
  detailTitle.textContent = stay.title;
  detailMeta.textContent = `${stay.guests} guests · ${stay.bedrooms} bedrooms · ${stay.beds} beds`;
  detailPrice.textContent = `$${stay.price_per_night} night`;
  listingDetail.hidden = false;

  const maxGuests = Number.parseInt(stay.guests, 10);
  bookingGuestsInput.max = String(maxGuests);
  bookingGuestsInput.value = String(Math.min(maxGuests, Number.parseInt(bookingGuestsInput.value, 10) || 1));
};

const fetchJson = async (url, options = {}) => {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || 'Request failed.');
  }

  return payload;
};

const loadStays = async () => {
  state.stays = await fetchJson('/api/stays');
};

const handleBookingSubmit = async (event) => {
  event.preventDefault();

  const fullName = userNameInput.value.trim();
  const email = userEmailInput.value.trim();
  const stayId = state.selectedStayId;
  const checkIn = checkInInput.value;
  const checkOut = checkOutInput.value;
  const guests = Number.parseInt(bookingGuestsInput.value, 10);

  const selectedStay = state.stays.find((stay) => stay.stay_id === stayId);
  if (!selectedStay) {
    message.textContent = 'Open a listing first, then submit the booking form.';
    return;
  }

  const maxGuests = Number.parseInt(selectedStay.guests, 10);
  if (guests > maxGuests) {
    message.textContent = `This stay supports up to ${maxGuests} guests.`;
    return;
  }

  try {
    const result = await fetchJson('/api/bookings', {
      method: 'POST',
      body: JSON.stringify({
        fullName,
        email,
        stayId,
        checkIn,
        checkOut,
        guests,
      }),
    });

    message.textContent = `Booking confirmed for ${result.stay.title}. Total: $${result.totalPrice}. Saved live to bookings.csv.`;
    bookingForm.reset();
    bookingGuestsInput.value = '2';
  } catch (error) {
    message.textContent = error.message;
  }
};

const handleCardsClick = (event) => {
  const favoriteButton = event.target.closest('.fav-btn');
  if (favoriteButton) {
    favoriteButton.classList.toggle('active');
    favoriteButton.textContent = favoriteButton.classList.contains('active') ? '❤' : '♡';
    return;
  }

  const bookButton = event.target.closest('.book-btn');
  if (bookButton) {
    selectStay(bookButton.dataset.stayId);
    listingDetail.scrollIntoView({ behavior: 'smooth', block: 'start' });
    message.textContent = 'Listing opened. Complete the form below to book this stay.';
  }
};

const handleSearch = () => {
  const destination = whereInput.value.trim().toLowerCase();

  if (!destination) {
    renderStays(state.stays);
    message.textContent = `Showing all ${state.stays.length} stays.`;
    return;
  }

  const filtered = state.stays.filter((stay) =>
    `${stay.location} ${stay.title}`.toLowerCase().includes(destination)
  );

  renderStays(filtered);
  message.textContent = `Showing ${filtered.length} stay(s) matching "${whereInput.value.trim()}".`;
};

const init = async () => {
  try {
    await loadStays();
    renderStays(state.stays);
    if (state.stays.length) {
      selectStay(state.stays[0].stay_id);
    }
    message.textContent = `Loaded ${state.stays.length} stays from live CSV backend.`;
  } catch (error) {
    message.textContent =
      'Could not connect to backend. Start the local server with "/Users/admin/march_cohort_2026/.venv/bin/python server.py" and open http://127.0.0.1:3000.';
  }
};

searchButton.addEventListener('click', handleSearch);
cardsContainer.addEventListener('click', handleCardsClick);
bookingForm.addEventListener('submit', handleBookingSubmit);

init();
