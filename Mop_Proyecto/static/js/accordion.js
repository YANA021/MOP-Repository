document.addEventListener('DOMContentLoaded', () => {
  const headers = document.querySelectorAll('#accordion-step3 .accordion-header');
  headers.forEach((btn) => {
    btn.addEventListener('click', () => {
      const item = btn.parentElement;
      item.classList.toggle('open');
    });
  });
});