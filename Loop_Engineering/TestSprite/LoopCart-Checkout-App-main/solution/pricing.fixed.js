export const COUPON_RATES = {
  SAVE20: 0.2,
};

export function calculateCart({ subtotal, couponCode }) {
  const normalizedCode = couponCode.trim().toUpperCase();
  const discountRate = COUPON_RATES[normalizedCode] ?? 0;
  const discount = subtotal * discountRate;
  const shipping = subtotal >= 75 ? 0 : 8;
  const total = Math.max(0, subtotal - discount + shipping);

  return {
    subtotal,
    discount,
    shipping,
    total,
    isValidCoupon: Boolean(COUPON_RATES[normalizedCode]),
  };
}
