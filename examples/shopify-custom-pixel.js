/*
 * Shopify Custom Pixel example.
 * This is a reference snippet: replace the endpoint only in a controlled,
 * consent-reviewed implementation. No real IDs or credentials are included.
 */

const eventMap = {
  page_viewed: "page_view",
  product_viewed: "view_item",
  product_added_to_cart: "add_to_cart",
  checkout_started: "begin_checkout",
  payment_info_submitted: "add_payment_info",
  checkout_completed: "purchase",
};

analytics.subscribe("all_standard_events", (shopifyEvent) => {
  const name = eventMap[shopifyEvent.name];
  if (!name) return;

  const payload = {
    name,
    event_id: shopifyEvent.id || crypto.randomUUID(),
    client_id: browser.cookie.get("demo_client_id") || "demo-client",
    source: "shopify_web_pixel",
    occurred_at: new Date().toISOString(),
    properties: shopifyEvent.data || {},
    // Populate from the store's consent solution; default-deny is safest.
    consent: {
      analytics_storage: false,
      ad_storage: false,
      ad_user_data: false,
      ad_personalization: false,
    },
  };

  fetch("https://measure.example.com/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    keepalive: true,
  });
});
