# LoopCart Product Requirement

## Product goal
LoopCart is a small checkout page used to demonstrate a closed AI coding loop.

## Required behavior
1. The cart starts with two products totaling exactly $100.00.
2. Orders with a subtotal of at least $75.00 receive free shipping.
3. Entering coupon code `SAVE20` and selecting **Apply coupon** must:
   - show a confirmation message;
   - apply a 20% discount;
   - display a discount of `-$20.00`;
   - display a final total of `$80.00`.
4. Selecting **Complete checkout** confirms the displayed total.

## Known demo regression
The starter version intentionally applies a 2% discount instead of 20%. The expected automated fix is in `src/pricing.js`.
