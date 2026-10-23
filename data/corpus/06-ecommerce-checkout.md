# E-Commerce Checkout and Payments

The checkout flow converts a shopping basket into a paid order. It typically collects the delivery address, selects a delivery method, takes payment, and only then creates the confirmed order record. Each step is validated before the customer can proceed, so an order is never confirmed with an invalid address or an unauthorised payment.

Payment requests use idempotency keys to stay safe under retries. An idempotency key is a unique value the client generates for one purchase attempt and sends with the payment request. If the network fails and the client retries, the payment provider sees the same key and returns the original result instead of charging the card twice. Idempotency keys therefore prevent duplicate charges when customers refresh the page, double-click the pay button, or lose connectivity at the moment of payment.

Card details never touch the merchant's own servers in a modern integration. The browser sends card data directly to the payment provider and receives a token, and the merchant stores only the token. This keeps the merchant within the lightest tier of card-industry compliance requirements.

Abandoned-checkout recovery is usually done with a timed email sequence. A first reminder is sent roughly one hour after abandonment, and it contains a direct link that restores the customer's basket exactly as they left it.

Fraud screening runs before fulfilment. Orders are scored on signals such as mismatched billing and delivery countries, unusually large first orders, and many failed payment attempts, and high-scoring orders are held for manual review instead of being shipped immediately.
