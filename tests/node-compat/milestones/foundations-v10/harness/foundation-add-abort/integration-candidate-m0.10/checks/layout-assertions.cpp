// Compile-only assertions. Never linked or executed.
#include "builtins/web/event/event-target.h"
#include "builtins/web/abort/abort-signal.h"

#ifdef NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER
static constexpr int kExpectedParentSlots = 2;
#else
static constexpr int kExpectedParentSlots = 1;
#endif
static_assert(std::to_underlying(builtins::web::event::EventTarget::Slots::Count) == kExpectedParentSlots);
static_assert(builtins::web::abort::AbortSignal::ParentSlots == kExpectedParentSlots);
static_assert(std::to_underlying(builtins::web::abort::AbortSignal::Slots::Reason) == kExpectedParentSlots);
