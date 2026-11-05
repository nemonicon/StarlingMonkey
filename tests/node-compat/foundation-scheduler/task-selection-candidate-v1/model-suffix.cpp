static void example(std::initializer_list<int> ids, std::vector<size_t> ready_indices,
                    std::optional<size_t> selected, std::vector<int> expected_ids,
                    std::vector<std::vector<int>> expected_polls, int expected_subscriptions) {
  immediately_ready.reset(); polls.clear(); subscriptions = 0; ready = std::move(ready_indices);
  std::vector<RefPtr<api::AsyncTask>> tasks;
  for (int id : ids) tasks.push_back(std::make_shared<api::AsyncTask>(id));
  assert(api::AsyncTask::select(tasks) == selected);
  std::vector<int> actual_ids;
  for (auto task : tasks) actual_ids.push_back(task->id());
  assert(actual_ids == expected_ids);
  assert(polls == expected_polls);
  assert(subscriptions == expected_subscriptions);
}
int main() {
  example({}, {}, std::nullopt, {}, {}, 0);
  example({-1}, {}, std::nullopt, {}, {}, 0);
  example({-1,-1,-1}, {}, std::nullopt, {}, {}, 0);
  example({-1,10,-1}, {0}, 0, {10}, {{10}}, 0);
  example({-1,10,-1,20}, {1,0}, 0, {10,20}, {{10,20}}, 0);
  example({10,20}, {1}, 1, {10,20}, {{10,20}}, 0);
  example({-2,10}, {}, 0, {-2,10}, {}, 0);
  example({10,-2,20}, {1}, 1, {10,-2,20}, {{10,77}}, 1);
  example({10,-2,20}, {1,0}, 0, {10,-2,20}, {{10,77}}, 1);
  example({-1,10,20,-2}, {2}, 2, {10,20,-2}, {{10,20,77}}, 1);
  // A cached immediate pollable is reused by the unchanged mixed-ready branch.
  std::vector<RefPtr<api::AsyncTask>> mixed = {
    std::make_shared<api::AsyncTask>(10), std::make_shared<api::AsyncTask>(-2)};
  ready = {1};
  assert(api::AsyncTask::select(mixed) == 1 && subscriptions == 1);
  // Safe abstract counterexample: the instrumented poll throws before touching
  // an empty result. The real baseline poll or guest is never executed here.
  bool refused = false;
  std::vector<RefPtr<api::LegacyAsyncTask>> old = {std::make_shared<api::LegacyAsyncTask>(-1)};
  try { (void)api::LegacyAsyncTask::select(old); }
  catch (const std::logic_error& e) { refused = std::string(e.what()) == "instrumented-empty-poll"; }
  assert(refused && old.empty());
  std::cout << "{\"schemaVersion\":1,\"cases\":12,\"allPassed\":true,"
    "\"abstractHostModelOnly\":true,\"guestExecuted\":false}\n";
}
