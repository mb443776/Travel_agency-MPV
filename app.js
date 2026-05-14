let currentIdx = 0, autoPlay = null;

function updateView(n) {
  const items = document.querySelectorAll('.carousel-item');
  if (!items.length) return;
  currentIdx = (n + items.length) % items.length;
  items.forEach((item, i) => item.classList.toggle('visible', i === currentIdx));
}

const moveNext = () => updateView(currentIdx + 1);
const movePrev = () => updateView(currentIdx - 1);

function runCarousel() {
  updateView(0);
  if (autoPlay) clearInterval(autoPlay);
  autoPlay = setInterval(moveNext, 3500); // Интервал чуть больше
}

function notify(text) {
  const box = document.querySelector('#alert-box');
  if (!box) return;
  box.innerText = text;
  box.classList.add('active');
  setTimeout(() => box.classList.remove('active'), 2000);
}

document.addEventListener('DOMContentLoaded', () => {
  runCarousel();
  
  document.querySelectorAll('[data-msg]').forEach(btn => {
    btn.onclick = () => notify(btn.dataset.msg || 'Успешно');
  });
});