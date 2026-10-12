import { calculateCart } from './pricing.js';

const subtotal = 100;
const money = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
});

const couponForm = document.querySelector('#coupon-form');
const couponInput = document.querySelector('#coupon');
const couponMessage = document.querySelector('#coupon-message');
const discountElement = document.querySelector('#discount');
const shippingElement = document.querySelector('#shipping');
const totalElement = document.querySelector('#total');
const checkoutButton = document.querySelector('#checkout-button');
const checkoutStatus = document.querySelector('#checkout-status');

let currentTotal = subtotal;

function renderTotals(result) {
  discountElement.textContent = `-${money.format(result.discount)}`;
  shippingElement.textContent = result.shipping === 0 ? 'Free' : money.format(result.shipping);
  totalElement.textContent = money.format(result.total);
  currentTotal = result.total;
}

couponForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const couponCode = couponInput.value.trim().toUpperCase();
  const result = calculateCart({ subtotal, couponCode });

  if (!result.isValidCoupon) {
    couponMessage.textContent = 'Coupon not found. Try SAVE20.';
    renderTotals(calculateCart({ subtotal, couponCode: '' }));
    return;
  }

  couponMessage.textContent = `Coupon ${couponCode} applied.`;
  renderTotals(result);
});

checkoutButton.addEventListener('click', () => {
  checkoutStatus.textContent = `Order confirmed for ${money.format(currentTotal)}.`;
});
