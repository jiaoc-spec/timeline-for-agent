const test = require("node:test");
const assert = require("node:assert/strict");

const { buildTimelineViews } = require("../src/infra/timeline/timeline-analytics");
const { createDefaultTaxonomy } = require("../src/infra/timeline/default-taxonomy");

test("phone screen time overlaps are counted once in analytics", () => {
  const state = {
    timezone: "Europe/Berlin",
    taxonomy: createDefaultTaxonomy(),
    facts: {
      "2026-06-05": {
        events: [
          phoneEvent("iphone", "2026-06-05T10:00:00+02:00", "2026-06-05T11:00:00+02:00", "iPhone"),
          phoneEvent("ipad", "2026-06-05T10:30:00+02:00", "2026-06-05T11:30:00+02:00", "iPad"),
        ],
      },
    },
  };

  const views = buildTimelineViews(state, {}, { locale: "zh-CN" });
  const day = views.ranges.day["2026-06-05"];
  const entertainment = day.categories.find((item) => item.categoryId === "entertainment");
  const phone = day.subcategoryDetails["entertainment.social_media"];

  assert.equal(entertainment.minutes, 90);
  assert.equal(phone.trend.find((bucket) => bucket.key === "10").minutes, 60);
  assert.equal(phone.trend.find((bucket) => bucket.key === "11").minutes, 30);
});

function phoneEvent(id, startAt, endAt, device) {
  return {
    id,
    title: `${device} 屏幕时间`,
    startAt,
    endAt,
    categoryId: "entertainment",
    subcategoryId: "entertainment.social_media",
    eventNodeId: "evt.phone_scroll",
    tags: ["phone", "screen-time", device.toLowerCase()],
  };
}
