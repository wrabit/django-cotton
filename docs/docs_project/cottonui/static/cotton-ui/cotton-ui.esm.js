// js/accordion.js
var accordion_default = (type, collapsible, disabled) => ({
  value: type == "single" ? "" : [],
  type,
  disabled,
  collapsible
});

// js/accordionItem.js
var accordionItem_default = () => ({
  root: {
    ["x-id"]() {
      return ["accordion-item"];
    }
  },
  trigger: {
    ["@click"]() {
      return this.toggle();
    },
    [":aria-expanded"]() {
      return this.$data.value.includes(this.$id("accordion-item"));
    },
    [":aria-controls"]() {
      return this.$id("accordion-item") + "-content";
    },
    [":id"]() {
      return this.$id("accordion-item") + "-trigger";
    },
    [":disabled"]() {
      return this.$data.disabled;
    }
  },
  icon: {
    [":class"]() {
      return { "-rotate-180": this.$data.value.includes(this.$id("accordion-item")) };
    }
  },
  content: {
    [":id"]() {
      return this.$id("accordion-item") + "-content";
    },
    [":aria-labelledby"]() {
      return this.$id("accordion-item") + "-trigger";
    },
    ["x-show"]() {
      return this.$data.value.includes(this.$id("accordion-item"));
    },
    ["x-collapse.duration.300ms"]() {
      return true;
    }
  },
  expand() {
    if (this.$data.type === "single") {
      this.$data.value = this.$id("accordion-item");
    }
    this.$nextTick(() => {
      this.$dispatch("valueChange", { value: this.$data.value });
    });
  },
  collapse() {
    if (this.$data.type === "single" && this.collapsible) {
      this.$data.value = "";
    }
    this.$nextTick(() => {
      this.$dispatch("valueChange", { value: this.$data.value });
    });
  },
  toggle() {
    this.$data.value.includes(this.$id("accordion-item")) ? this.collapse() : this.expand();
  }
});

// js/alert.js
var alert_default = (dismissOnTimeout, timeout, startTimeoutOnIntersect) => ({
  "visible": true,
  "dismissOnTimeout": dismissOnTimeout,
  "startTimeoutOnIntersect": startTimeoutOnIntersect,
  "timeout": timeout,
  root: {
    ["x-show"]() {
      return this.visible;
    },
    ["x-cloak"]() {
      return true;
    },
    ["x-transition"]() {
      return true;
    },
    ["x-intersect"]() {
      if (this.dismissOnTimeout && this.startTimeoutOnIntersect) {
        return setTimeout(() => {
          this.dismiss();
        }, this.timeout);
      }
    }
  },
  dismissTrigger: {
    ["@click"]() {
      return this.dismiss();
    }
  },
  init() {
    if (this.dismissOnTimeout && !this.startTimeoutOnIntersect) {
      setTimeout(() => {
        this.dismiss();
      }, this.timeout);
    }
  },
  dismiss() {
    this.visible = false;
  }
});

// js/avatar.js
var avatar_default = () => ({
  loadSuccess: false,
  image: {
    ["x-show"]() {
      return this.loadSuccess;
    },
    ["x-cloak"]() {
      return true;
    },
    ["x-on:load"]() {
      return this.loadSuccess = true;
    }
  },
  fallback: {
    ["x-show"]() {
      return !this.loadSuccess;
    },
    ["x-cloak"]() {
      return true;
    }
  }
});

// js/banner.js
var banner_default = (displayAfter, transitionEnterStart, transitionEnterEnd, transitionLeaveStart, transitionLeaveEnd) => ({
  visible: false,
  displayAfter,
  transitionEnterStart,
  transitionEnterEnd,
  transitionLeaveStart,
  transitionLeaveEnd,
  root: {
    ["x-show"]() {
      return this.visible;
    },
    ["x-cloak"]() {
      return true;
    },
    ["x-transition:enter"]() {
      return "transition ease-out duration-500";
    },
    ["x-transition:enter-start"]() {
      return this.transitionEnterStart;
    },
    ["x-transition:enter-end"]() {
      return this.transitionEnterEnd;
    },
    ["x-transition:leave"]() {
      return "transition ease-in duration-300";
    },
    ["x-transition:leave-start"]() {
      return this.transitionLeaveStart;
    },
    ["x-transition:leave-end"]() {
      return this.transitionLeaveEnd;
    }
  },
  dismissTrigger: {
    ["@click"]() {
      return this.dismiss();
    }
  },
  init() {
    setTimeout(() => {
      this.display();
    }, this.displayAfter);
  },
  display() {
    this.visible = true;
  },
  dismiss() {
    this.visible = false;
  }
});

// js/Calendar/Matcher.js
var Matcher = class {
  constructor(rule) {
    this.type = this.determineMatcherType(rule);
    this.rule = rule;
  }
  passes(date) {
    date = this.createDateWithoutTime(date);
    if (this.type == "dates") {
      return this.rule.dates.some((element) => date.getTime() == this.createDateWithoutTime(element).getTime());
    } else if (this.type == "range") {
      if (this.rule.before != null && date.getTime() < this.createDateWithoutTime(this.rule.before).getTime()) {
        return true;
      }
      if (this.rule.after != null && date.getTime() > this.createDateWithoutTime(this.rule.after).getTime()) {
        return true;
      }
      return false;
    } else if (this.type == "dayOfWeek") {
      if (typeof this.rule.dayOfWeek == "number") {
        return date.getDay() == this.rule.dayOfWeek;
      } else {
        return this.rule.dayOfWeek.some((rule) => rule == date.getDay());
      }
    }
    return false;
  }
  determineMatcherType(rule) {
    if (rule.dates != void 0 && Array.isArray(rule.dates)) {
      return "dates";
    } else if (rule.before != void 0 || rule.after != void 0) {
      return "range";
    } else if (rule.dayOfWeek != void 0) {
      return "dayOfWeek";
    }
  }
  createDateWithoutTime(value) {
    let date = new Date(value);
    date.setHours(0, 0, 0, 0);
    return date;
  }
};

// js/Calendar/ModeHandlers/MultipleModeHandler.js
var MultipleModeHandler = class {
  constructor(required, min, max) {
    this.min = min;
    this.max = max;
    this._value = [];
    this.required = !!required;
  }
  get value() {
    return this._value;
  }
  set value(value) {
    if (!Array.isArray(value)) {
      console.warn("Selected type supplied to calendar in multiple mode is not an array");
      return;
    }
    value.forEach((item) => {
      const processDate = (input) => {
        if (input == null)
          return null;
        if (typeof input === "string")
          return this.createDateWithoutTime(input);
        if (input instanceof Date)
          return input;
        console.warn("Item is not a date or date string, skipping");
        return null;
      };
      item = processDate(item);
      if (this.isSelectedDay(item)) {
        return;
      }
      this._value.push(item);
    });
  }
  isDisabled(date) {
    if (this.max && this.max <= this._value.length) {
      return !this.isSelectedDay(date);
    }
  }
  indexOfDateInValue(array, value) {
    for (let index = 0; index < array.length; index++) {
      const date = array[index];
      if (date.getTime() === value.getTime()) {
        return index;
      }
    }
    return -1;
  }
  dayClicked(date) {
    let index = this.indexOfDateInValue(this._value, date);
    if (index >= 0) {
      this._value.splice(index, 1);
    } else {
      this._value.push(date);
    }
    return true;
  }
  isSelectedDay(date) {
    return this.indexOfDateInValue(this._value, date) >= 0;
  }
  createDateWithoutTime(value) {
    let date = new Date(value);
    date.setHours(0, 0, 0, 0);
    return date;
  }
};

// js/Calendar/ModeHandlers/RangeModeHandler.js
var RangeModeHandler = class {
  constructor(required, min, max) {
    this.min = min;
    this.max = max;
    this.required = !!required;
  }
  dayClicked(date) {
    if (this._value.from == null || this._value.to != null && this._value.to.getTime() == date.getTime()) {
      this._value.from = date;
      this._value.to = null;
      return true;
    }
    if (this._value.from.getTime() == date.getTime()) {
      this._value.from = this.required ? this._value.from : null;
      this._value.to = null;
      return true;
    }
    if (this._value.from.getTime() >= date.getTime()) {
      this._value.from = date;
      return true;
    }
    this._value.to = date;
    return true;
  }
  isSelectedDay(date) {
    if (this._value.from == null) {
      return false;
    }
    if (this._value.to == null) {
      return this._value.from.getTime() == date.getTime();
    }
    return date.getTime() == this._value.from.getTime() || date.getTime() == this._value.to.getTime();
  }
  get value() {
    return this._value;
  }
  set value(value) {
    if (this._value == null) {
      this._value = { from: null, to: null };
    }
    if (value == null) {
      return;
    }
    const processDate = (input) => {
      if (input == null)
        return null;
      if (typeof input === "string")
        return this.createDateWithoutTime(input);
      if (input instanceof Date)
        return input;
      console.warn("Item is not a date or date string, skipping");
      return null;
    };
    this._value.from = processDate(value.from);
    this._value.to = processDate(value.to);
  }
  isDisabled(date) {
    if (this._value.from) {
      let daysBetween = Math.abs(this.getNumberOfDaysBetweenDates(this._value.from, date));
      return (this.min && daysBetween < this.min || this.max && daysBetween > this.max) && daysBetween != 0;
    }
  }
  isRangeMiddle(date) {
    if (this._value.from && this._value.to && date.getTime() >= this._value.from.getTime() && date.getTime() <= this._value.to.getTime()) {
      return true;
    }
    return false;
  }
  createDateWithoutTime(value) {
    let date = new Date(value);
    date.setHours(0, 0, 0, 0);
    return date;
  }
  getNumberOfDaysBetweenDates(date1, date2) {
    return Math.round((date1.getTime() - date2.getTime()) / (1e3 * 3600 * 24));
  }
};

// js/Calendar/ModeHandlers/SingleModeHandler.js
var SingleModeHandler = class {
  constructor(required) {
    this.required = !!required;
  }
  get value() {
    return this._value;
  }
  set value(value) {
    const processDate = (input) => {
      if (input == null)
        return null;
      if (typeof input === "string")
        return this.createDateWithoutTime(input);
      if (input instanceof Date)
        return input;
      console.warn("Item is not a date or date string, skipping");
      return null;
    };
    this._value = processDate(value);
  }
  dayClicked(date) {
    if (this._value != null && this._value.getTime() == date.getTime() && !this.required) {
      this._value = null;
    } else {
      this._value = date;
    }
    return true;
  }
  isSelectedDay(date) {
    return this._value?.getTime() === date.getTime();
  }
  isDisabled(date) {
    return false;
  }
  createDateWithoutTime(value) {
    let date = new Date(value);
    date.setHours(0, 0, 0, 0);
    return date;
  }
};

// js/calendar.js
var calendar_default = (selected, mode, disabled, min, max, required) => ({
  focusedDay: "",
  mode,
  max,
  min,
  month: "",
  year: "",
  daysInMonth: [],
  preBlankDaysInMonth: [],
  postBlankDaysInMonth: [],
  modeHandler: null,
  disabled: [],
  monthNames: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  days: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  root: {
    ["@keydown.left.prevent"]() {
      this.focusAdd(-1);
    },
    ["@keydown.right.prevent"]() {
      this.focusAdd(1);
    },
    ["@keydown.up.prevent"]() {
      this.focusAdd(-this.days.length);
    },
    ["@keydown.down.prevent"]() {
      this.focusAdd(this.days.length);
    },
    ["x-transition"]() {
      return true;
    }
  },
  previousMonthTrigger: {
    ["@click"]() {
      this.previousMonth();
    }
  },
  nextMonthTrigger: {
    ["@click"]() {
      this.nextMonth();
    }
  },
  yearLabel: {
    ["x-text"]() {
      return this.year;
    }
  },
  monthLabel: {
    ["x-text"]() {
      return this.monthNames[this.month];
    }
  },
  init() {
    if (this.mode == "single") {
      this.modeHandler = new SingleModeHandler(required);
    } else if (this.mode == "multiple") {
      this.modeHandler = new MultipleModeHandler(required, min, max);
    } else if (this.mode == "range") {
      this.modeHandler = new RangeModeHandler(required, min, max);
    } else {
      console.error("Mode is invalid, defaulting to single mode");
      this.modeHandler = new SingleModeHandler(required);
    }
    if (Array.isArray(disabled)) {
      disabled.forEach((element) => {
        this.disabled.push(new Matcher(element));
      });
    } else if (typeof disabled == "object" && disabled != null) {
      this.disabled = [new Matcher(disabled)];
    }
    let now = new Date();
    this.month = now.getMonth();
    this.year = now.getFullYear();
    this.focusedDay = now.getDay();
    this.calculateDays();
    if (!!selected) {
      this.dispatchChange();
    }
  },
  dispatchChange() {
    this.$nextTick(() => {
      this.$dispatch("change", { value: this.modeHandler.value });
    });
  },
  dayClicked(date) {
    let selectedDate = new Date(this.year, this.month, date);
    if (this.isDisabled(selectedDate)) {
      return;
    }
    this.focusedDay = date;
    let dispatchEvent = this.modeHandler.dayClicked(selectedDate);
    if (dispatchEvent) {
      this.dispatchChange();
    }
  },
  focusAdd(value) {
    if (!Number.isInteger(this.focusedDay)) {
      this.focusedDay = new Date(this.year, this.month, day).getDate();
    }
    this.focusedDay = this.focusedDay + value;
    if (this.focusedDay > this.daysInMonth.length) {
      this.focusedDay = this.focusedDay - this.daysInMonth.length;
      this.nextMonth();
    } else if (this.focusedDay <= 0) {
      this.previousMonth();
      this.focusedDay = this.daysInMonth.length + this.focusedDay;
    }
  },
  previousMonth() {
    if (this.month == 0) {
      this.year--;
      this.month = 12;
    }
    this.month--;
    this.calculateDays();
  },
  nextMonth() {
    if (this.month == 11) {
      this.month = 0;
      this.year++;
    } else {
      this.month++;
    }
    this.calculateDays();
  },
  isSelectedDay(day2) {
    let date = new Date(this.year, this.month, day2);
    return this.modeHandler.isSelectedDay(date);
  },
  isFocusedDate(day2) {
    return this.focusedDay === day2 ? true : false;
  },
  isToday(day2) {
    const today = new Date();
    const d = new Date(this.year, this.month, day2);
    return today.toDateString() === d.toDateString() ? true : false;
  },
  calculateDays() {
    let daysInMonth = new Date(this.year, this.month + 1, 0).getDate();
    let daysInPreviousMonth = new Date(this.year, this.month, 0).getDate();
    let dayOfWeek = new Date(this.year, this.month).getDay();
    let preBlankdaysArray = [];
    for (var i = 1; i <= dayOfWeek; i++) {
      preBlankdaysArray.push(daysInPreviousMonth - i + 1);
    }
    preBlankdaysArray = preBlankdaysArray.reverse();
    let postBlankdaysArray = [];
    for (var i = 1; i <= this.days.length * 6 - (preBlankdaysArray.length + daysInMonth); i++) {
      postBlankdaysArray.push(i);
    }
    let daysArray = [];
    for (var i = 1; i <= daysInMonth; i++) {
      daysArray.push(i);
    }
    this.preBlankDaysInMonth = preBlankdaysArray;
    this.postBlankDaysInMonth = postBlankdaysArray;
    this.daysInMonth = daysArray;
  },
  isDisabled(date) {
    return this.disabled.some((rule) => rule.passes(date)) || this.modeHandler.isDisabled(date);
  },
  isRangeMiddle(date) {
    if (mode == "range") {
      return this.modeHandler.isRangeMiddle(date);
    }
    return false;
  }
});

// js/command.js
var command_default = (value) => ({
  keyword: value,
  focusedItem: null,
  root: {
    ["@keydown"]($event) {
      if ($event.key == "Home") {
        this.selectOption(1, false);
      }
      if ($event.key == "End") {
        this.selectOption(-1, false);
      }
    },
    ["@keydown.capture.down.prevent"]() {
      this.selectOption(1);
    },
    ["@keydown.capture.up.prevent"]() {
      this.selectOption(-1);
    },
    ["@keydown.capture.enter.prevent"]() {
      if (this.focusedItem != null) {
        this.focusedItem.click();
      }
    }
  },
  init() {
    this.$nextTick(() => {
      this.selectOption(0, false);
    });
  },
  commandInput: {
    ["@input"]() {
      this.keyword = this.$el.value;
      this.$nextTick(() => {
        this.selectOption(0, false);
      });
      this.$dispatch("valueChange", { value: this.keyword });
    },
    [":id"]() {
      return this.$id("command") + "-input";
    },
    [":aria-controls"]() {
      return this.$id("command") + "-list";
    }
  },
  commandList: {
    [":id"]() {
      return this.$id("command") + "-list";
    }
  },
  commandItem: {
    [":data-cmd-item"]() {
      return true;
    },
    [":data-selected"]() {
      return this.$el.contains(this.focusedItem);
    },
    [":aria-selected"]() {
      return this.$el.contains(this.focusedItem);
    },
    [":tabindex"]() {
      return this.$el.contains(this.focusedItem) ? 0 : -1;
    },
    ["x-effect"]() {
      if (this.keyword == "" || this.fuzzySearch(this.keyword, this.$el.innerText)) {
        this.$el.dataset.active = true;
        this.$el.style.display = "flex";
      } else {
        this.$el.dataset.active = false;
        this.$el.style.display = "none";
      }
    },
    ["@mouseenter"]() {
      return this.focusedItem = this.$el;
    }
  },
  commandGroupHeading: {
    [":id"]() {
      return this.$id("command") + "-group-heading";
    }
  },
  commandGroup: {
    [":id"]() {
      return this.$id("command") + "-group";
    },
    [":aria-labelledby"]() {
      return this.$id("command") + "-group-heading";
    }
  },
  commandGroupContainer: {
    ["x-effect"]() {
      this.keyword == "";
      this.$nextTick(() => {
        this.$el.style.display = this.$el.querySelectorAll("[data-active=true]").length > 0 ? "block" : "none";
      });
    }
  },
  commandEmpty: {
    ["x-effect"]() {
      this.keyword == "";
      this.$nextTick(() => {
        this.$el.style.display = this.$refs.list.querySelectorAll("[data-active=true]").length > 0 ? "none" : "block";
      });
    }
  },
  selectOption(index, relative = true) {
    let nodeList = this.$refs.list.querySelectorAll("[data-active=true]");
    let nodeListArray = Array.from(nodeList);
    let initialIndex = index;
    if (nodeList.length == 0 || !nodeListArray.some((node) => JSON.parse(node.dataset.disabled) == false)) {
      return;
    }
    if (relative) {
      let previousIndex = Array.from(nodeList).findIndex((node) => node.isEqualNode(this.focusedItem)) ?? 0;
      index += previousIndex;
    }
    index += index < 0 ? nodeList.length : 0;
    index = index % nodeList.length;
    while (JSON.parse(nodeList[index].dataset.disabled)) {
      index += initialIndex < 0 ? -1 : 1;
      index = index % nodeList.length;
    }
    this.focusedItem = nodeList[index];
    this.focusedItem.scrollIntoView(initialIndex < 0);
  },
  fuzzySearch(keyword, text) {
    const keywordLower = keyword.toLowerCase();
    const textLower = text.toLowerCase();
    let keywordIndex = 0;
    for (let i = 0; i < textLower.length; i++) {
      if (textLower[i] === keywordLower[keywordIndex]) {
        keywordIndex++;
      }
      if (keywordIndex === keywordLower.length) {
        return true;
      }
    }
    return false;
  }
});

// node_modules/date-fns/toDate.mjs
function toDate(argument) {
  const argStr = Object.prototype.toString.call(argument);
  if (argument instanceof Date || typeof argument === "object" && argStr === "[object Date]") {
    return new argument.constructor(+argument);
  } else if (typeof argument === "number" || argStr === "[object Number]" || typeof argument === "string" || argStr === "[object String]") {
    return new Date(argument);
  } else {
    return new Date(NaN);
  }
}

// node_modules/date-fns/constructFrom.mjs
function constructFrom(date, value) {
  if (date instanceof Date) {
    return new date.constructor(value);
  } else {
    return new Date(value);
  }
}

// node_modules/date-fns/constants.mjs
var daysInYear = 365.2425;
var maxTime = Math.pow(10, 8) * 24 * 60 * 60 * 1e3;
var minTime = -maxTime;
var millisecondsInWeek = 6048e5;
var millisecondsInDay = 864e5;
var secondsInHour = 3600;
var secondsInDay = secondsInHour * 24;
var secondsInWeek = secondsInDay * 7;
var secondsInYear = secondsInDay * daysInYear;
var secondsInMonth = secondsInYear / 12;
var secondsInQuarter = secondsInMonth * 3;

// node_modules/date-fns/_lib/defaultOptions.mjs
var defaultOptions = {};
function getDefaultOptions() {
  return defaultOptions;
}

// node_modules/date-fns/startOfWeek.mjs
function startOfWeek(date, options) {
  const defaultOptions2 = getDefaultOptions();
  const weekStartsOn = options?.weekStartsOn ?? options?.locale?.options?.weekStartsOn ?? defaultOptions2.weekStartsOn ?? defaultOptions2.locale?.options?.weekStartsOn ?? 0;
  const _date = toDate(date);
  const day2 = _date.getDay();
  const diff = (day2 < weekStartsOn ? 7 : 0) + day2 - weekStartsOn;
  _date.setDate(_date.getDate() - diff);
  _date.setHours(0, 0, 0, 0);
  return _date;
}

// node_modules/date-fns/startOfISOWeek.mjs
function startOfISOWeek(date) {
  return startOfWeek(date, { weekStartsOn: 1 });
}

// node_modules/date-fns/getISOWeekYear.mjs
function getISOWeekYear(date) {
  const _date = toDate(date);
  const year = _date.getFullYear();
  const fourthOfJanuaryOfNextYear = constructFrom(date, 0);
  fourthOfJanuaryOfNextYear.setFullYear(year + 1, 0, 4);
  fourthOfJanuaryOfNextYear.setHours(0, 0, 0, 0);
  const startOfNextYear = startOfISOWeek(fourthOfJanuaryOfNextYear);
  const fourthOfJanuaryOfThisYear = constructFrom(date, 0);
  fourthOfJanuaryOfThisYear.setFullYear(year, 0, 4);
  fourthOfJanuaryOfThisYear.setHours(0, 0, 0, 0);
  const startOfThisYear = startOfISOWeek(fourthOfJanuaryOfThisYear);
  if (_date.getTime() >= startOfNextYear.getTime()) {
    return year + 1;
  } else if (_date.getTime() >= startOfThisYear.getTime()) {
    return year;
  } else {
    return year - 1;
  }
}

// node_modules/date-fns/startOfDay.mjs
function startOfDay(date) {
  const _date = toDate(date);
  _date.setHours(0, 0, 0, 0);
  return _date;
}

// node_modules/date-fns/_lib/getTimezoneOffsetInMilliseconds.mjs
function getTimezoneOffsetInMilliseconds(date) {
  const _date = toDate(date);
  const utcDate = new Date(
    Date.UTC(
      _date.getFullYear(),
      _date.getMonth(),
      _date.getDate(),
      _date.getHours(),
      _date.getMinutes(),
      _date.getSeconds(),
      _date.getMilliseconds()
    )
  );
  utcDate.setUTCFullYear(_date.getFullYear());
  return +date - +utcDate;
}

// node_modules/date-fns/differenceInCalendarDays.mjs
function differenceInCalendarDays(dateLeft, dateRight) {
  const startOfDayLeft = startOfDay(dateLeft);
  const startOfDayRight = startOfDay(dateRight);
  const timestampLeft = +startOfDayLeft - getTimezoneOffsetInMilliseconds(startOfDayLeft);
  const timestampRight = +startOfDayRight - getTimezoneOffsetInMilliseconds(startOfDayRight);
  return Math.round((timestampLeft - timestampRight) / millisecondsInDay);
}

// node_modules/date-fns/startOfISOWeekYear.mjs
function startOfISOWeekYear(date) {
  const year = getISOWeekYear(date);
  const fourthOfJanuary = constructFrom(date, 0);
  fourthOfJanuary.setFullYear(year, 0, 4);
  fourthOfJanuary.setHours(0, 0, 0, 0);
  return startOfISOWeek(fourthOfJanuary);
}

// node_modules/date-fns/isDate.mjs
function isDate(value) {
  return value instanceof Date || typeof value === "object" && Object.prototype.toString.call(value) === "[object Date]";
}

// node_modules/date-fns/isValid.mjs
function isValid(date) {
  if (!isDate(date) && typeof date !== "number") {
    return false;
  }
  const _date = toDate(date);
  return !isNaN(Number(_date));
}

// node_modules/date-fns/startOfYear.mjs
function startOfYear(date) {
  const cleanDate = toDate(date);
  const _date = constructFrom(date, 0);
  _date.setFullYear(cleanDate.getFullYear(), 0, 1);
  _date.setHours(0, 0, 0, 0);
  return _date;
}

// node_modules/date-fns/locale/en-US/_lib/formatDistance.mjs
var formatDistanceLocale = {
  lessThanXSeconds: {
    one: "less than a second",
    other: "less than {{count}} seconds"
  },
  xSeconds: {
    one: "1 second",
    other: "{{count}} seconds"
  },
  halfAMinute: "half a minute",
  lessThanXMinutes: {
    one: "less than a minute",
    other: "less than {{count}} minutes"
  },
  xMinutes: {
    one: "1 minute",
    other: "{{count}} minutes"
  },
  aboutXHours: {
    one: "about 1 hour",
    other: "about {{count}} hours"
  },
  xHours: {
    one: "1 hour",
    other: "{{count}} hours"
  },
  xDays: {
    one: "1 day",
    other: "{{count}} days"
  },
  aboutXWeeks: {
    one: "about 1 week",
    other: "about {{count}} weeks"
  },
  xWeeks: {
    one: "1 week",
    other: "{{count}} weeks"
  },
  aboutXMonths: {
    one: "about 1 month",
    other: "about {{count}} months"
  },
  xMonths: {
    one: "1 month",
    other: "{{count}} months"
  },
  aboutXYears: {
    one: "about 1 year",
    other: "about {{count}} years"
  },
  xYears: {
    one: "1 year",
    other: "{{count}} years"
  },
  overXYears: {
    one: "over 1 year",
    other: "over {{count}} years"
  },
  almostXYears: {
    one: "almost 1 year",
    other: "almost {{count}} years"
  }
};
var formatDistance = (token, count, options) => {
  let result;
  const tokenValue = formatDistanceLocale[token];
  if (typeof tokenValue === "string") {
    result = tokenValue;
  } else if (count === 1) {
    result = tokenValue.one;
  } else {
    result = tokenValue.other.replace("{{count}}", count.toString());
  }
  if (options?.addSuffix) {
    if (options.comparison && options.comparison > 0) {
      return "in " + result;
    } else {
      return result + " ago";
    }
  }
  return result;
};

// node_modules/date-fns/locale/_lib/buildFormatLongFn.mjs
function buildFormatLongFn(args) {
  return (options = {}) => {
    const width = options.width ? String(options.width) : args.defaultWidth;
    const format2 = args.formats[width] || args.formats[args.defaultWidth];
    return format2;
  };
}

// node_modules/date-fns/locale/en-US/_lib/formatLong.mjs
var dateFormats = {
  full: "EEEE, MMMM do, y",
  long: "MMMM do, y",
  medium: "MMM d, y",
  short: "MM/dd/yyyy"
};
var timeFormats = {
  full: "h:mm:ss a zzzz",
  long: "h:mm:ss a z",
  medium: "h:mm:ss a",
  short: "h:mm a"
};
var dateTimeFormats = {
  full: "{{date}} 'at' {{time}}",
  long: "{{date}} 'at' {{time}}",
  medium: "{{date}}, {{time}}",
  short: "{{date}}, {{time}}"
};
var formatLong = {
  date: buildFormatLongFn({
    formats: dateFormats,
    defaultWidth: "full"
  }),
  time: buildFormatLongFn({
    formats: timeFormats,
    defaultWidth: "full"
  }),
  dateTime: buildFormatLongFn({
    formats: dateTimeFormats,
    defaultWidth: "full"
  })
};

// node_modules/date-fns/locale/en-US/_lib/formatRelative.mjs
var formatRelativeLocale = {
  lastWeek: "'last' eeee 'at' p",
  yesterday: "'yesterday at' p",
  today: "'today at' p",
  tomorrow: "'tomorrow at' p",
  nextWeek: "eeee 'at' p",
  other: "P"
};
var formatRelative = (token, _date, _baseDate, _options) => formatRelativeLocale[token];

// node_modules/date-fns/locale/_lib/buildLocalizeFn.mjs
function buildLocalizeFn(args) {
  return (value, options) => {
    const context = options?.context ? String(options.context) : "standalone";
    let valuesArray;
    if (context === "formatting" && args.formattingValues) {
      const defaultWidth = args.defaultFormattingWidth || args.defaultWidth;
      const width = options?.width ? String(options.width) : defaultWidth;
      valuesArray = args.formattingValues[width] || args.formattingValues[defaultWidth];
    } else {
      const defaultWidth = args.defaultWidth;
      const width = options?.width ? String(options.width) : args.defaultWidth;
      valuesArray = args.values[width] || args.values[defaultWidth];
    }
    const index = args.argumentCallback ? args.argumentCallback(value) : value;
    return valuesArray[index];
  };
}

// node_modules/date-fns/locale/en-US/_lib/localize.mjs
var eraValues = {
  narrow: ["B", "A"],
  abbreviated: ["BC", "AD"],
  wide: ["Before Christ", "Anno Domini"]
};
var quarterValues = {
  narrow: ["1", "2", "3", "4"],
  abbreviated: ["Q1", "Q2", "Q3", "Q4"],
  wide: ["1st quarter", "2nd quarter", "3rd quarter", "4th quarter"]
};
var monthValues = {
  narrow: ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
  abbreviated: [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
  ],
  wide: [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
  ]
};
var dayValues = {
  narrow: ["S", "M", "T", "W", "T", "F", "S"],
  short: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
  abbreviated: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  wide: [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
  ]
};
var dayPeriodValues = {
  narrow: {
    am: "a",
    pm: "p",
    midnight: "mi",
    noon: "n",
    morning: "morning",
    afternoon: "afternoon",
    evening: "evening",
    night: "night"
  },
  abbreviated: {
    am: "AM",
    pm: "PM",
    midnight: "midnight",
    noon: "noon",
    morning: "morning",
    afternoon: "afternoon",
    evening: "evening",
    night: "night"
  },
  wide: {
    am: "a.m.",
    pm: "p.m.",
    midnight: "midnight",
    noon: "noon",
    morning: "morning",
    afternoon: "afternoon",
    evening: "evening",
    night: "night"
  }
};
var formattingDayPeriodValues = {
  narrow: {
    am: "a",
    pm: "p",
    midnight: "mi",
    noon: "n",
    morning: "in the morning",
    afternoon: "in the afternoon",
    evening: "in the evening",
    night: "at night"
  },
  abbreviated: {
    am: "AM",
    pm: "PM",
    midnight: "midnight",
    noon: "noon",
    morning: "in the morning",
    afternoon: "in the afternoon",
    evening: "in the evening",
    night: "at night"
  },
  wide: {
    am: "a.m.",
    pm: "p.m.",
    midnight: "midnight",
    noon: "noon",
    morning: "in the morning",
    afternoon: "in the afternoon",
    evening: "in the evening",
    night: "at night"
  }
};
var ordinalNumber = (dirtyNumber, _options) => {
  const number = Number(dirtyNumber);
  const rem100 = number % 100;
  if (rem100 > 20 || rem100 < 10) {
    switch (rem100 % 10) {
      case 1:
        return number + "st";
      case 2:
        return number + "nd";
      case 3:
        return number + "rd";
    }
  }
  return number + "th";
};
var localize = {
  ordinalNumber,
  era: buildLocalizeFn({
    values: eraValues,
    defaultWidth: "wide"
  }),
  quarter: buildLocalizeFn({
    values: quarterValues,
    defaultWidth: "wide",
    argumentCallback: (quarter) => quarter - 1
  }),
  month: buildLocalizeFn({
    values: monthValues,
    defaultWidth: "wide"
  }),
  day: buildLocalizeFn({
    values: dayValues,
    defaultWidth: "wide"
  }),
  dayPeriod: buildLocalizeFn({
    values: dayPeriodValues,
    defaultWidth: "wide",
    formattingValues: formattingDayPeriodValues,
    defaultFormattingWidth: "wide"
  })
};

// node_modules/date-fns/locale/_lib/buildMatchFn.mjs
function buildMatchFn(args) {
  return (string, options = {}) => {
    const width = options.width;
    const matchPattern = width && args.matchPatterns[width] || args.matchPatterns[args.defaultMatchWidth];
    const matchResult = string.match(matchPattern);
    if (!matchResult) {
      return null;
    }
    const matchedString = matchResult[0];
    const parsePatterns = width && args.parsePatterns[width] || args.parsePatterns[args.defaultParseWidth];
    const key = Array.isArray(parsePatterns) ? findIndex(parsePatterns, (pattern) => pattern.test(matchedString)) : findKey(parsePatterns, (pattern) => pattern.test(matchedString));
    let value;
    value = args.valueCallback ? args.valueCallback(key) : key;
    value = options.valueCallback ? options.valueCallback(value) : value;
    const rest = string.slice(matchedString.length);
    return { value, rest };
  };
}
function findKey(object, predicate) {
  for (const key in object) {
    if (Object.prototype.hasOwnProperty.call(object, key) && predicate(object[key])) {
      return key;
    }
  }
  return void 0;
}
function findIndex(array, predicate) {
  for (let key = 0; key < array.length; key++) {
    if (predicate(array[key])) {
      return key;
    }
  }
  return void 0;
}

// node_modules/date-fns/locale/_lib/buildMatchPatternFn.mjs
function buildMatchPatternFn(args) {
  return (string, options = {}) => {
    const matchResult = string.match(args.matchPattern);
    if (!matchResult)
      return null;
    const matchedString = matchResult[0];
    const parseResult = string.match(args.parsePattern);
    if (!parseResult)
      return null;
    let value = args.valueCallback ? args.valueCallback(parseResult[0]) : parseResult[0];
    value = options.valueCallback ? options.valueCallback(value) : value;
    const rest = string.slice(matchedString.length);
    return { value, rest };
  };
}

// node_modules/date-fns/locale/en-US/_lib/match.mjs
var matchOrdinalNumberPattern = /^(\d+)(th|st|nd|rd)?/i;
var parseOrdinalNumberPattern = /\d+/i;
var matchEraPatterns = {
  narrow: /^(b|a)/i,
  abbreviated: /^(b\.?\s?c\.?|b\.?\s?c\.?\s?e\.?|a\.?\s?d\.?|c\.?\s?e\.?)/i,
  wide: /^(before christ|before common era|anno domini|common era)/i
};
var parseEraPatterns = {
  any: [/^b/i, /^(a|c)/i]
};
var matchQuarterPatterns = {
  narrow: /^[1234]/i,
  abbreviated: /^q[1234]/i,
  wide: /^[1234](th|st|nd|rd)? quarter/i
};
var parseQuarterPatterns = {
  any: [/1/i, /2/i, /3/i, /4/i]
};
var matchMonthPatterns = {
  narrow: /^[jfmasond]/i,
  abbreviated: /^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)/i,
  wide: /^(january|february|march|april|may|june|july|august|september|october|november|december)/i
};
var parseMonthPatterns = {
  narrow: [
    /^j/i,
    /^f/i,
    /^m/i,
    /^a/i,
    /^m/i,
    /^j/i,
    /^j/i,
    /^a/i,
    /^s/i,
    /^o/i,
    /^n/i,
    /^d/i
  ],
  any: [
    /^ja/i,
    /^f/i,
    /^mar/i,
    /^ap/i,
    /^may/i,
    /^jun/i,
    /^jul/i,
    /^au/i,
    /^s/i,
    /^o/i,
    /^n/i,
    /^d/i
  ]
};
var matchDayPatterns = {
  narrow: /^[smtwf]/i,
  short: /^(su|mo|tu|we|th|fr|sa)/i,
  abbreviated: /^(sun|mon|tue|wed|thu|fri|sat)/i,
  wide: /^(sunday|monday|tuesday|wednesday|thursday|friday|saturday)/i
};
var parseDayPatterns = {
  narrow: [/^s/i, /^m/i, /^t/i, /^w/i, /^t/i, /^f/i, /^s/i],
  any: [/^su/i, /^m/i, /^tu/i, /^w/i, /^th/i, /^f/i, /^sa/i]
};
var matchDayPeriodPatterns = {
  narrow: /^(a|p|mi|n|(in the|at) (morning|afternoon|evening|night))/i,
  any: /^([ap]\.?\s?m\.?|midnight|noon|(in the|at) (morning|afternoon|evening|night))/i
};
var parseDayPeriodPatterns = {
  any: {
    am: /^a/i,
    pm: /^p/i,
    midnight: /^mi/i,
    noon: /^no/i,
    morning: /morning/i,
    afternoon: /afternoon/i,
    evening: /evening/i,
    night: /night/i
  }
};
var match = {
  ordinalNumber: buildMatchPatternFn({
    matchPattern: matchOrdinalNumberPattern,
    parsePattern: parseOrdinalNumberPattern,
    valueCallback: (value) => parseInt(value, 10)
  }),
  era: buildMatchFn({
    matchPatterns: matchEraPatterns,
    defaultMatchWidth: "wide",
    parsePatterns: parseEraPatterns,
    defaultParseWidth: "any"
  }),
  quarter: buildMatchFn({
    matchPatterns: matchQuarterPatterns,
    defaultMatchWidth: "wide",
    parsePatterns: parseQuarterPatterns,
    defaultParseWidth: "any",
    valueCallback: (index) => index + 1
  }),
  month: buildMatchFn({
    matchPatterns: matchMonthPatterns,
    defaultMatchWidth: "wide",
    parsePatterns: parseMonthPatterns,
    defaultParseWidth: "any"
  }),
  day: buildMatchFn({
    matchPatterns: matchDayPatterns,
    defaultMatchWidth: "wide",
    parsePatterns: parseDayPatterns,
    defaultParseWidth: "any"
  }),
  dayPeriod: buildMatchFn({
    matchPatterns: matchDayPeriodPatterns,
    defaultMatchWidth: "any",
    parsePatterns: parseDayPeriodPatterns,
    defaultParseWidth: "any"
  })
};

// node_modules/date-fns/locale/en-US.mjs
var enUS = {
  code: "en-US",
  formatDistance,
  formatLong,
  formatRelative,
  localize,
  match,
  options: {
    weekStartsOn: 0,
    firstWeekContainsDate: 1
  }
};

// node_modules/date-fns/getDayOfYear.mjs
function getDayOfYear(date) {
  const _date = toDate(date);
  const diff = differenceInCalendarDays(_date, startOfYear(_date));
  const dayOfYear = diff + 1;
  return dayOfYear;
}

// node_modules/date-fns/getISOWeek.mjs
function getISOWeek(date) {
  const _date = toDate(date);
  const diff = +startOfISOWeek(_date) - +startOfISOWeekYear(_date);
  return Math.round(diff / millisecondsInWeek) + 1;
}

// node_modules/date-fns/getWeekYear.mjs
function getWeekYear(date, options) {
  const _date = toDate(date);
  const year = _date.getFullYear();
  const defaultOptions2 = getDefaultOptions();
  const firstWeekContainsDate = options?.firstWeekContainsDate ?? options?.locale?.options?.firstWeekContainsDate ?? defaultOptions2.firstWeekContainsDate ?? defaultOptions2.locale?.options?.firstWeekContainsDate ?? 1;
  const firstWeekOfNextYear = constructFrom(date, 0);
  firstWeekOfNextYear.setFullYear(year + 1, 0, firstWeekContainsDate);
  firstWeekOfNextYear.setHours(0, 0, 0, 0);
  const startOfNextYear = startOfWeek(firstWeekOfNextYear, options);
  const firstWeekOfThisYear = constructFrom(date, 0);
  firstWeekOfThisYear.setFullYear(year, 0, firstWeekContainsDate);
  firstWeekOfThisYear.setHours(0, 0, 0, 0);
  const startOfThisYear = startOfWeek(firstWeekOfThisYear, options);
  if (_date.getTime() >= startOfNextYear.getTime()) {
    return year + 1;
  } else if (_date.getTime() >= startOfThisYear.getTime()) {
    return year;
  } else {
    return year - 1;
  }
}

// node_modules/date-fns/startOfWeekYear.mjs
function startOfWeekYear(date, options) {
  const defaultOptions2 = getDefaultOptions();
  const firstWeekContainsDate = options?.firstWeekContainsDate ?? options?.locale?.options?.firstWeekContainsDate ?? defaultOptions2.firstWeekContainsDate ?? defaultOptions2.locale?.options?.firstWeekContainsDate ?? 1;
  const year = getWeekYear(date, options);
  const firstWeek = constructFrom(date, 0);
  firstWeek.setFullYear(year, 0, firstWeekContainsDate);
  firstWeek.setHours(0, 0, 0, 0);
  const _date = startOfWeek(firstWeek, options);
  return _date;
}

// node_modules/date-fns/getWeek.mjs
function getWeek(date, options) {
  const _date = toDate(date);
  const diff = +startOfWeek(_date, options) - +startOfWeekYear(_date, options);
  return Math.round(diff / millisecondsInWeek) + 1;
}

// node_modules/date-fns/_lib/addLeadingZeros.mjs
function addLeadingZeros(number, targetLength) {
  const sign = number < 0 ? "-" : "";
  const output = Math.abs(number).toString().padStart(targetLength, "0");
  return sign + output;
}

// node_modules/date-fns/_lib/format/lightFormatters.mjs
var lightFormatters = {
  y(date, token) {
    const signedYear = date.getFullYear();
    const year = signedYear > 0 ? signedYear : 1 - signedYear;
    return addLeadingZeros(token === "yy" ? year % 100 : year, token.length);
  },
  M(date, token) {
    const month = date.getMonth();
    return token === "M" ? String(month + 1) : addLeadingZeros(month + 1, 2);
  },
  d(date, token) {
    return addLeadingZeros(date.getDate(), token.length);
  },
  a(date, token) {
    const dayPeriodEnumValue = date.getHours() / 12 >= 1 ? "pm" : "am";
    switch (token) {
      case "a":
      case "aa":
        return dayPeriodEnumValue.toUpperCase();
      case "aaa":
        return dayPeriodEnumValue;
      case "aaaaa":
        return dayPeriodEnumValue[0];
      case "aaaa":
      default:
        return dayPeriodEnumValue === "am" ? "a.m." : "p.m.";
    }
  },
  h(date, token) {
    return addLeadingZeros(date.getHours() % 12 || 12, token.length);
  },
  H(date, token) {
    return addLeadingZeros(date.getHours(), token.length);
  },
  m(date, token) {
    return addLeadingZeros(date.getMinutes(), token.length);
  },
  s(date, token) {
    return addLeadingZeros(date.getSeconds(), token.length);
  },
  S(date, token) {
    const numberOfDigits = token.length;
    const milliseconds = date.getMilliseconds();
    const fractionalSeconds = Math.trunc(
      milliseconds * Math.pow(10, numberOfDigits - 3)
    );
    return addLeadingZeros(fractionalSeconds, token.length);
  }
};

// node_modules/date-fns/_lib/format/formatters.mjs
var dayPeriodEnum = {
  am: "am",
  pm: "pm",
  midnight: "midnight",
  noon: "noon",
  morning: "morning",
  afternoon: "afternoon",
  evening: "evening",
  night: "night"
};
var formatters = {
  G: function(date, token, localize2) {
    const era = date.getFullYear() > 0 ? 1 : 0;
    switch (token) {
      case "G":
      case "GG":
      case "GGG":
        return localize2.era(era, { width: "abbreviated" });
      case "GGGGG":
        return localize2.era(era, { width: "narrow" });
      case "GGGG":
      default:
        return localize2.era(era, { width: "wide" });
    }
  },
  y: function(date, token, localize2) {
    if (token === "yo") {
      const signedYear = date.getFullYear();
      const year = signedYear > 0 ? signedYear : 1 - signedYear;
      return localize2.ordinalNumber(year, { unit: "year" });
    }
    return lightFormatters.y(date, token);
  },
  Y: function(date, token, localize2, options) {
    const signedWeekYear = getWeekYear(date, options);
    const weekYear = signedWeekYear > 0 ? signedWeekYear : 1 - signedWeekYear;
    if (token === "YY") {
      const twoDigitYear = weekYear % 100;
      return addLeadingZeros(twoDigitYear, 2);
    }
    if (token === "Yo") {
      return localize2.ordinalNumber(weekYear, { unit: "year" });
    }
    return addLeadingZeros(weekYear, token.length);
  },
  R: function(date, token) {
    const isoWeekYear = getISOWeekYear(date);
    return addLeadingZeros(isoWeekYear, token.length);
  },
  u: function(date, token) {
    const year = date.getFullYear();
    return addLeadingZeros(year, token.length);
  },
  Q: function(date, token, localize2) {
    const quarter = Math.ceil((date.getMonth() + 1) / 3);
    switch (token) {
      case "Q":
        return String(quarter);
      case "QQ":
        return addLeadingZeros(quarter, 2);
      case "Qo":
        return localize2.ordinalNumber(quarter, { unit: "quarter" });
      case "QQQ":
        return localize2.quarter(quarter, {
          width: "abbreviated",
          context: "formatting"
        });
      case "QQQQQ":
        return localize2.quarter(quarter, {
          width: "narrow",
          context: "formatting"
        });
      case "QQQQ":
      default:
        return localize2.quarter(quarter, {
          width: "wide",
          context: "formatting"
        });
    }
  },
  q: function(date, token, localize2) {
    const quarter = Math.ceil((date.getMonth() + 1) / 3);
    switch (token) {
      case "q":
        return String(quarter);
      case "qq":
        return addLeadingZeros(quarter, 2);
      case "qo":
        return localize2.ordinalNumber(quarter, { unit: "quarter" });
      case "qqq":
        return localize2.quarter(quarter, {
          width: "abbreviated",
          context: "standalone"
        });
      case "qqqqq":
        return localize2.quarter(quarter, {
          width: "narrow",
          context: "standalone"
        });
      case "qqqq":
      default:
        return localize2.quarter(quarter, {
          width: "wide",
          context: "standalone"
        });
    }
  },
  M: function(date, token, localize2) {
    const month = date.getMonth();
    switch (token) {
      case "M":
      case "MM":
        return lightFormatters.M(date, token);
      case "Mo":
        return localize2.ordinalNumber(month + 1, { unit: "month" });
      case "MMM":
        return localize2.month(month, {
          width: "abbreviated",
          context: "formatting"
        });
      case "MMMMM":
        return localize2.month(month, {
          width: "narrow",
          context: "formatting"
        });
      case "MMMM":
      default:
        return localize2.month(month, { width: "wide", context: "formatting" });
    }
  },
  L: function(date, token, localize2) {
    const month = date.getMonth();
    switch (token) {
      case "L":
        return String(month + 1);
      case "LL":
        return addLeadingZeros(month + 1, 2);
      case "Lo":
        return localize2.ordinalNumber(month + 1, { unit: "month" });
      case "LLL":
        return localize2.month(month, {
          width: "abbreviated",
          context: "standalone"
        });
      case "LLLLL":
        return localize2.month(month, {
          width: "narrow",
          context: "standalone"
        });
      case "LLLL":
      default:
        return localize2.month(month, { width: "wide", context: "standalone" });
    }
  },
  w: function(date, token, localize2, options) {
    const week = getWeek(date, options);
    if (token === "wo") {
      return localize2.ordinalNumber(week, { unit: "week" });
    }
    return addLeadingZeros(week, token.length);
  },
  I: function(date, token, localize2) {
    const isoWeek = getISOWeek(date);
    if (token === "Io") {
      return localize2.ordinalNumber(isoWeek, { unit: "week" });
    }
    return addLeadingZeros(isoWeek, token.length);
  },
  d: function(date, token, localize2) {
    if (token === "do") {
      return localize2.ordinalNumber(date.getDate(), { unit: "date" });
    }
    return lightFormatters.d(date, token);
  },
  D: function(date, token, localize2) {
    const dayOfYear = getDayOfYear(date);
    if (token === "Do") {
      return localize2.ordinalNumber(dayOfYear, { unit: "dayOfYear" });
    }
    return addLeadingZeros(dayOfYear, token.length);
  },
  E: function(date, token, localize2) {
    const dayOfWeek = date.getDay();
    switch (token) {
      case "E":
      case "EE":
      case "EEE":
        return localize2.day(dayOfWeek, {
          width: "abbreviated",
          context: "formatting"
        });
      case "EEEEE":
        return localize2.day(dayOfWeek, {
          width: "narrow",
          context: "formatting"
        });
      case "EEEEEE":
        return localize2.day(dayOfWeek, {
          width: "short",
          context: "formatting"
        });
      case "EEEE":
      default:
        return localize2.day(dayOfWeek, {
          width: "wide",
          context: "formatting"
        });
    }
  },
  e: function(date, token, localize2, options) {
    const dayOfWeek = date.getDay();
    const localDayOfWeek = (dayOfWeek - options.weekStartsOn + 8) % 7 || 7;
    switch (token) {
      case "e":
        return String(localDayOfWeek);
      case "ee":
        return addLeadingZeros(localDayOfWeek, 2);
      case "eo":
        return localize2.ordinalNumber(localDayOfWeek, { unit: "day" });
      case "eee":
        return localize2.day(dayOfWeek, {
          width: "abbreviated",
          context: "formatting"
        });
      case "eeeee":
        return localize2.day(dayOfWeek, {
          width: "narrow",
          context: "formatting"
        });
      case "eeeeee":
        return localize2.day(dayOfWeek, {
          width: "short",
          context: "formatting"
        });
      case "eeee":
      default:
        return localize2.day(dayOfWeek, {
          width: "wide",
          context: "formatting"
        });
    }
  },
  c: function(date, token, localize2, options) {
    const dayOfWeek = date.getDay();
    const localDayOfWeek = (dayOfWeek - options.weekStartsOn + 8) % 7 || 7;
    switch (token) {
      case "c":
        return String(localDayOfWeek);
      case "cc":
        return addLeadingZeros(localDayOfWeek, token.length);
      case "co":
        return localize2.ordinalNumber(localDayOfWeek, { unit: "day" });
      case "ccc":
        return localize2.day(dayOfWeek, {
          width: "abbreviated",
          context: "standalone"
        });
      case "ccccc":
        return localize2.day(dayOfWeek, {
          width: "narrow",
          context: "standalone"
        });
      case "cccccc":
        return localize2.day(dayOfWeek, {
          width: "short",
          context: "standalone"
        });
      case "cccc":
      default:
        return localize2.day(dayOfWeek, {
          width: "wide",
          context: "standalone"
        });
    }
  },
  i: function(date, token, localize2) {
    const dayOfWeek = date.getDay();
    const isoDayOfWeek = dayOfWeek === 0 ? 7 : dayOfWeek;
    switch (token) {
      case "i":
        return String(isoDayOfWeek);
      case "ii":
        return addLeadingZeros(isoDayOfWeek, token.length);
      case "io":
        return localize2.ordinalNumber(isoDayOfWeek, { unit: "day" });
      case "iii":
        return localize2.day(dayOfWeek, {
          width: "abbreviated",
          context: "formatting"
        });
      case "iiiii":
        return localize2.day(dayOfWeek, {
          width: "narrow",
          context: "formatting"
        });
      case "iiiiii":
        return localize2.day(dayOfWeek, {
          width: "short",
          context: "formatting"
        });
      case "iiii":
      default:
        return localize2.day(dayOfWeek, {
          width: "wide",
          context: "formatting"
        });
    }
  },
  a: function(date, token, localize2) {
    const hours = date.getHours();
    const dayPeriodEnumValue = hours / 12 >= 1 ? "pm" : "am";
    switch (token) {
      case "a":
      case "aa":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "abbreviated",
          context: "formatting"
        });
      case "aaa":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "abbreviated",
          context: "formatting"
        }).toLowerCase();
      case "aaaaa":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "narrow",
          context: "formatting"
        });
      case "aaaa":
      default:
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "wide",
          context: "formatting"
        });
    }
  },
  b: function(date, token, localize2) {
    const hours = date.getHours();
    let dayPeriodEnumValue;
    if (hours === 12) {
      dayPeriodEnumValue = dayPeriodEnum.noon;
    } else if (hours === 0) {
      dayPeriodEnumValue = dayPeriodEnum.midnight;
    } else {
      dayPeriodEnumValue = hours / 12 >= 1 ? "pm" : "am";
    }
    switch (token) {
      case "b":
      case "bb":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "abbreviated",
          context: "formatting"
        });
      case "bbb":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "abbreviated",
          context: "formatting"
        }).toLowerCase();
      case "bbbbb":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "narrow",
          context: "formatting"
        });
      case "bbbb":
      default:
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "wide",
          context: "formatting"
        });
    }
  },
  B: function(date, token, localize2) {
    const hours = date.getHours();
    let dayPeriodEnumValue;
    if (hours >= 17) {
      dayPeriodEnumValue = dayPeriodEnum.evening;
    } else if (hours >= 12) {
      dayPeriodEnumValue = dayPeriodEnum.afternoon;
    } else if (hours >= 4) {
      dayPeriodEnumValue = dayPeriodEnum.morning;
    } else {
      dayPeriodEnumValue = dayPeriodEnum.night;
    }
    switch (token) {
      case "B":
      case "BB":
      case "BBB":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "abbreviated",
          context: "formatting"
        });
      case "BBBBB":
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "narrow",
          context: "formatting"
        });
      case "BBBB":
      default:
        return localize2.dayPeriod(dayPeriodEnumValue, {
          width: "wide",
          context: "formatting"
        });
    }
  },
  h: function(date, token, localize2) {
    if (token === "ho") {
      let hours = date.getHours() % 12;
      if (hours === 0)
        hours = 12;
      return localize2.ordinalNumber(hours, { unit: "hour" });
    }
    return lightFormatters.h(date, token);
  },
  H: function(date, token, localize2) {
    if (token === "Ho") {
      return localize2.ordinalNumber(date.getHours(), { unit: "hour" });
    }
    return lightFormatters.H(date, token);
  },
  K: function(date, token, localize2) {
    const hours = date.getHours() % 12;
    if (token === "Ko") {
      return localize2.ordinalNumber(hours, { unit: "hour" });
    }
    return addLeadingZeros(hours, token.length);
  },
  k: function(date, token, localize2) {
    let hours = date.getHours();
    if (hours === 0)
      hours = 24;
    if (token === "ko") {
      return localize2.ordinalNumber(hours, { unit: "hour" });
    }
    return addLeadingZeros(hours, token.length);
  },
  m: function(date, token, localize2) {
    if (token === "mo") {
      return localize2.ordinalNumber(date.getMinutes(), { unit: "minute" });
    }
    return lightFormatters.m(date, token);
  },
  s: function(date, token, localize2) {
    if (token === "so") {
      return localize2.ordinalNumber(date.getSeconds(), { unit: "second" });
    }
    return lightFormatters.s(date, token);
  },
  S: function(date, token) {
    return lightFormatters.S(date, token);
  },
  X: function(date, token, _localize) {
    const timezoneOffset = date.getTimezoneOffset();
    if (timezoneOffset === 0) {
      return "Z";
    }
    switch (token) {
      case "X":
        return formatTimezoneWithOptionalMinutes(timezoneOffset);
      case "XXXX":
      case "XX":
        return formatTimezone(timezoneOffset);
      case "XXXXX":
      case "XXX":
      default:
        return formatTimezone(timezoneOffset, ":");
    }
  },
  x: function(date, token, _localize) {
    const timezoneOffset = date.getTimezoneOffset();
    switch (token) {
      case "x":
        return formatTimezoneWithOptionalMinutes(timezoneOffset);
      case "xxxx":
      case "xx":
        return formatTimezone(timezoneOffset);
      case "xxxxx":
      case "xxx":
      default:
        return formatTimezone(timezoneOffset, ":");
    }
  },
  O: function(date, token, _localize) {
    const timezoneOffset = date.getTimezoneOffset();
    switch (token) {
      case "O":
      case "OO":
      case "OOO":
        return "GMT" + formatTimezoneShort(timezoneOffset, ":");
      case "OOOO":
      default:
        return "GMT" + formatTimezone(timezoneOffset, ":");
    }
  },
  z: function(date, token, _localize) {
    const timezoneOffset = date.getTimezoneOffset();
    switch (token) {
      case "z":
      case "zz":
      case "zzz":
        return "GMT" + formatTimezoneShort(timezoneOffset, ":");
      case "zzzz":
      default:
        return "GMT" + formatTimezone(timezoneOffset, ":");
    }
  },
  t: function(date, token, _localize) {
    const timestamp = Math.trunc(date.getTime() / 1e3);
    return addLeadingZeros(timestamp, token.length);
  },
  T: function(date, token, _localize) {
    const timestamp = date.getTime();
    return addLeadingZeros(timestamp, token.length);
  }
};
function formatTimezoneShort(offset, delimiter = "") {
  const sign = offset > 0 ? "-" : "+";
  const absOffset = Math.abs(offset);
  const hours = Math.trunc(absOffset / 60);
  const minutes = absOffset % 60;
  if (minutes === 0) {
    return sign + String(hours);
  }
  return sign + String(hours) + delimiter + addLeadingZeros(minutes, 2);
}
function formatTimezoneWithOptionalMinutes(offset, delimiter) {
  if (offset % 60 === 0) {
    const sign = offset > 0 ? "-" : "+";
    return sign + addLeadingZeros(Math.abs(offset) / 60, 2);
  }
  return formatTimezone(offset, delimiter);
}
function formatTimezone(offset, delimiter = "") {
  const sign = offset > 0 ? "-" : "+";
  const absOffset = Math.abs(offset);
  const hours = addLeadingZeros(Math.trunc(absOffset / 60), 2);
  const minutes = addLeadingZeros(absOffset % 60, 2);
  return sign + hours + delimiter + minutes;
}

// node_modules/date-fns/_lib/format/longFormatters.mjs
var dateLongFormatter = (pattern, formatLong2) => {
  switch (pattern) {
    case "P":
      return formatLong2.date({ width: "short" });
    case "PP":
      return formatLong2.date({ width: "medium" });
    case "PPP":
      return formatLong2.date({ width: "long" });
    case "PPPP":
    default:
      return formatLong2.date({ width: "full" });
  }
};
var timeLongFormatter = (pattern, formatLong2) => {
  switch (pattern) {
    case "p":
      return formatLong2.time({ width: "short" });
    case "pp":
      return formatLong2.time({ width: "medium" });
    case "ppp":
      return formatLong2.time({ width: "long" });
    case "pppp":
    default:
      return formatLong2.time({ width: "full" });
  }
};
var dateTimeLongFormatter = (pattern, formatLong2) => {
  const matchResult = pattern.match(/(P+)(p+)?/) || [];
  const datePattern = matchResult[1];
  const timePattern = matchResult[2];
  if (!timePattern) {
    return dateLongFormatter(pattern, formatLong2);
  }
  let dateTimeFormat;
  switch (datePattern) {
    case "P":
      dateTimeFormat = formatLong2.dateTime({ width: "short" });
      break;
    case "PP":
      dateTimeFormat = formatLong2.dateTime({ width: "medium" });
      break;
    case "PPP":
      dateTimeFormat = formatLong2.dateTime({ width: "long" });
      break;
    case "PPPP":
    default:
      dateTimeFormat = formatLong2.dateTime({ width: "full" });
      break;
  }
  return dateTimeFormat.replace("{{date}}", dateLongFormatter(datePattern, formatLong2)).replace("{{time}}", timeLongFormatter(timePattern, formatLong2));
};
var longFormatters = {
  p: timeLongFormatter,
  P: dateTimeLongFormatter
};

// node_modules/date-fns/_lib/protectedTokens.mjs
var dayOfYearTokenRE = /^D+$/;
var weekYearTokenRE = /^Y+$/;
var throwTokens = ["D", "DD", "YY", "YYYY"];
function isProtectedDayOfYearToken(token) {
  return dayOfYearTokenRE.test(token);
}
function isProtectedWeekYearToken(token) {
  return weekYearTokenRE.test(token);
}
function warnOrThrowProtectedError(token, format2, input) {
  const _message = message(token, format2, input);
  console.warn(_message);
  if (throwTokens.includes(token))
    throw new RangeError(_message);
}
function message(token, format2, input) {
  const subject = token[0] === "Y" ? "years" : "days of the month";
  return `Use \`${token.toLowerCase()}\` instead of \`${token}\` (in \`${format2}\`) for formatting ${subject} to the input \`${input}\`; see: https://github.com/date-fns/date-fns/blob/master/docs/unicodeTokens.md`;
}

// node_modules/date-fns/format.mjs
var formattingTokensRegExp = /[yYQqMLwIdDecihHKkms]o|(\w)\1*|''|'(''|[^'])+('|$)|./g;
var longFormattingTokensRegExp = /P+p+|P+|p+|''|'(''|[^'])+('|$)|./g;
var escapedStringRegExp = /^'([^]*?)'?$/;
var doubleQuoteRegExp = /''/g;
var unescapedLatinCharacterRegExp = /[a-zA-Z]/;
function format(date, formatStr, options) {
  const defaultOptions2 = getDefaultOptions();
  const locale = options?.locale ?? defaultOptions2.locale ?? enUS;
  const firstWeekContainsDate = options?.firstWeekContainsDate ?? options?.locale?.options?.firstWeekContainsDate ?? defaultOptions2.firstWeekContainsDate ?? defaultOptions2.locale?.options?.firstWeekContainsDate ?? 1;
  const weekStartsOn = options?.weekStartsOn ?? options?.locale?.options?.weekStartsOn ?? defaultOptions2.weekStartsOn ?? defaultOptions2.locale?.options?.weekStartsOn ?? 0;
  const originalDate = toDate(date);
  if (!isValid(originalDate)) {
    throw new RangeError("Invalid time value");
  }
  let parts = formatStr.match(longFormattingTokensRegExp).map((substring) => {
    const firstCharacter = substring[0];
    if (firstCharacter === "p" || firstCharacter === "P") {
      const longFormatter = longFormatters[firstCharacter];
      return longFormatter(substring, locale.formatLong);
    }
    return substring;
  }).join("").match(formattingTokensRegExp).map((substring) => {
    if (substring === "''") {
      return { isToken: false, value: "'" };
    }
    const firstCharacter = substring[0];
    if (firstCharacter === "'") {
      return { isToken: false, value: cleanEscapedString(substring) };
    }
    if (formatters[firstCharacter]) {
      return { isToken: true, value: substring };
    }
    if (firstCharacter.match(unescapedLatinCharacterRegExp)) {
      throw new RangeError(
        "Format string contains an unescaped latin alphabet character `" + firstCharacter + "`"
      );
    }
    return { isToken: false, value: substring };
  });
  if (locale.localize.preprocessor) {
    parts = locale.localize.preprocessor(originalDate, parts);
  }
  const formatterOptions = {
    firstWeekContainsDate,
    weekStartsOn,
    locale
  };
  return parts.map((part) => {
    if (!part.isToken)
      return part.value;
    const token = part.value;
    if (!options?.useAdditionalWeekYearTokens && isProtectedWeekYearToken(token) || !options?.useAdditionalDayOfYearTokens && isProtectedDayOfYearToken(token)) {
      warnOrThrowProtectedError(token, formatStr, String(date));
    }
    const formatter = formatters[token[0]];
    return formatter(originalDate, token, locale.localize, formatterOptions);
  }).join("");
}
function cleanEscapedString(input) {
  const matched = input.match(escapedStringRegExp);
  if (!matched) {
    return input;
  }
  return matched[1].replace(doubleQuoteRegExp, "'");
}

// js/datePicker.js
var datePicker_default = (open, value, mode, format2) => ({
  open,
  value: null,
  mode,
  format: format2,
  root: {
    ["@keydown.esc"]() {
      return this.closePicker();
    },
    ["x-cloak"]() {
      return true;
    }
  },
  trigger: {
    ["@click"]() {
      return this.togglePicker();
    },
    ["@keyup.esc"]() {
      return this.closePicker();
    },
    ["@keydown.space"]() {
      return this.togglePicker();
    },
    [":class"]() {
      return !this.value && "text-muted-foreground";
    }
  },
  calendar: {
    ["x-show"]() {
      return this.open;
    },
    ["x-cloak"]() {
      return true;
    },
    ["x-transition"]() {
      return true;
    },
    ["@click.away"]() {
      return this.closePicker();
    },
    ["x-anchor.bottom-start.offset.3"]() {
      return this.$refs.datePickerInput;
    },
    ["x-trap"]() {
      return this.open;
    }
  },
  init() {
    this.value = value;
  },
  openPicker() {
    this.open = true;
  },
  closePicker() {
    this.open = false;
  },
  togglePicker() {
    this.open ? this.closePicker() : this.openPicker();
  },
  formatDate(date) {
    if (date == null) {
      return null;
    }
    return format(new Date(date), this.format);
  }
});

// js/dialog.js
var dialog_default = (show, dismissable) => ({
  show,
  dismissable,
  close() {
    this.show = false;
  },
  open() {
    this.show = true;
  },
  root: {
    ["x-id"]() {
      return ["dialog"];
    },
    ["x-on:keydown.esc.window.stop"]() {
      if (this.dismissable) {
        return this.close();
      }
    }
  },
  trigger: {
    ["@click"]() {
      return this.open();
    },
    [":id"]() {
      return this.$id("dialog") + "-trigger";
    }
  },
  overlay: {
    ["@click"]() {
      if (this.dismissable) {
        return this.close();
      }
    },
    ["x-show"]() {
      return this.show;
    },
    ["x-cloak"]() {
      return true;
    },
    ["x-trap.noscroll.inert"]() {
      return this.show;
    },
    ["x-transition.opacity.duration.150ms"]() {
      return true;
    }
  },
  dialog: {
    ["@click.stop"]() {
      return true;
    },
    [":aria-labelledby"]() {
      return this.$id("dialog") + "-title";
    },
    [":aria-describedby"]() {
      return this.$id("dialog") + "-description";
    },
    [":aria-modal"]() {
      return this.show;
    }
  },
  title: {
    [":id"]() {
      return this.$id("dialog") + "-title";
    }
  },
  description: {
    [":id"]() {
      return this.$id("dialog") + "-description";
    }
  },
  closeButton: {
    ["@click"]() {
      if (this.dismissable) {
        return this.close();
      }
    }
  }
});

// js/dropdownMenu.js
var dropdownMenu_default = () => ({
  dropdownMenu: false,
  root: {
    ["x-id"]() {
      return ["dropdown-menu"];
    },
    ["@click.outside.capture"]() {
      if (!this.$refs.content.contains(this.$event.target) && !this.$refs.trigger.contains(this.$event.target)) {
        return this.close();
      }
    }
  },
  trigger: {
    ["@click"]() {
      return this.toggle();
    },
    ["@keydown.down.prevent"]() {
      if (!this.$refs.content.contains(document.activeElement)) {
        return this.$focus.focus(this.$refs.content.querySelector("button") ?? null);
      }
      return this.$focus.within(this.$refs.content).wrap().next();
    },
    ["@keydown.up.prevent"]() {
      if (!this.$refs.content.contains(document.activeElement)) {
        return this.$focus.focus([...this.$refs.content.querySelectorAll("button")].pop() || null);
      }
      return this.$focus.within(this.$refs.content).wrap().previous();
    },
    ["@keydown"]($event) {
      if ($event.key == "Home") {
        if (!this.$refs.content.contains(document.activeElement)) {
          return this.$focus.focus(this.$refs.content.querySelector("button") ?? null);
        }
        return this.$focus.within(this.$refs.content).wrap().first();
      }
      if ($event.key == "End") {
        if (!this.$refs.content.contains(document.activeElement)) {
          return this.$focus.focus([...this.$refs.content.querySelectorAll("button")].pop() || null);
        }
        return this.$focus.within(this.$refs.content).wrap().last();
      }
    },
    [":id"]() {
      return this.$id("dropdown-menu") + "-trigger";
    },
    [":aria-controls"]() {
      return this.$id("dropdown-menu") + "-content";
    },
    ["@keydown.esc.window"]() {
      return this.close();
    }
  },
  content: {
    ["x-anchor.offset.4"]() {
      return this.$refs.trigger;
    },
    ["@keydown.down.prevent"]() {
      if (!this.$refs.content.contains(document.activeElement)) {
        return this.$focus.focus(this.$refs.content.querySelector("button") ?? null);
      }
      return this.$focus.within(this.$refs.content).wrap().next();
    },
    ["@keydown.up.prevent"]() {
      if (!this.$refs.content.contains(document.activeElement)) {
        return this.$focus.focus([...this.$refs.content.querySelectorAll("button")].pop() || null);
      }
      return this.$focus.within(this.$refs.content).wrap().previous();
    },
    ["@keydown"]($event) {
      if ($event.key == "Home") {
        if (!this.$refs.content.contains(document.activeElement)) {
          return this.$focus.focus(this.$refs.content.querySelector("button") ?? null);
        }
        return this.$focus.within(this.$refs.content).wrap().first();
      }
      if ($event.key == "End") {
        if (!this.$refs.content.contains(document.activeElement)) {
          return this.$focus.focus([...this.$refs.content.querySelectorAll("button")].pop() || null);
        }
        return this.$focus.within(this.$refs.content).wrap().last();
      }
    },
    [":id"]() {
      return this.$id("dropdown-menu") + "-content";
    },
    [":aria-labelledby"]() {
      return this.$id("dropdown-menu") + "-trigger";
    },
    ["x-trap.noscroll.noautofocus"]() {
      return this.dropdownMenu;
    },
    ["x-show"]() {
      return this.dropdownMenu;
    },
    ["x-transition"]() {
      return true;
    }
  },
  menuItem: {
    ["@click"]() {
      return this.close();
    },
    ["@mouseover"]() {
      return this.$focus.focus(this.$el);
    },
    ["@focus"]() {
      this.$el.setAttribute("tabindex", 0);
    },
    ["@focusout"]() {
      this.$el.setAttribute("tabindex", -1);
    },
    ["@keydown.tab"]() {
      this.close();
    }
  },
  close() {
    this.dropdownMenu = false;
  },
  open() {
    this.dropdownMenu = true;
  },
  toggle() {
    this.dropdownMenu ? this.close() : this.open();
  }
});

// js/dropdownMenuSub.js
var dropdownMenuSub_default = () => ({
  subOpen: false,
  subPreview: false,
  root: {
    ["@keydown.escape"]() {
      return this.closeSub();
    },
    ["@click.outside"]() {
      return this.closeSub();
    },
    ["@keydown.right"]() {
      return this.open();
    },
    [":aria-expanded"]() {
      return this.subOpen;
    },
    ["@mouseleave"]() {
      this.closePreview();
    }
  },
  trigger: {
    ["@click.capture.stop"]() {
      return this.open();
    },
    ["@mouseenter"]() {
      this.openPreview();
      this.$focus.focus(this.$el);
    },
    ["@focus"]() {
      this.$el.setAttribute("tabindex", 0);
    },
    ["@focusout"]() {
      this.$el.setAttribute("tabindex", -1);
    }
  },
  template: {
    ["x-if"]() {
      return this.subOpen || this.subPreview;
    }
  },
  content: {
    ["x-anchor.right-start.no-style"]() {
      return this.$refs.subTrigger;
    },
    [":style"]() {
      let correction = 0;
      if (this.$anchor.x + this.$refs.content.scrollWidth > window.innerWidth) {
        correction = this.$refs.content.getBoundingClientRect().width / 2;
      } else if (this.$anchor.x - this.$refs.subTrigger.getBoundingClientRect().width <= 0) {
        correction = -this.$refs.content.getBoundingClientRect().width;
      }
      return { position: "absolute", top: this.$anchor.y + "px", left: this.$anchor.x - correction + "px" };
    },
    ["x-trap"]() {
      return this.subOpen;
    },
    ["x-show"]() {
      return this.subOpen || this.subPreview;
    },
    ["x-transition"]() {
      return true;
    },
    ["x-cloak"]() {
      return true;
    },
    ["@keydown.down.prevent"]() {
      return this.$focus.wrap().next();
    },
    ["@keydown.up.prevent"]() {
      return this.$focus.wrap().previous();
    },
    ["@keydown"]($event) {
      if ($event.key == "Home") {
        return this.$focus.wrap().first();
      }
      if ($event.key == "End") {
        return this.$focus.wrap().last();
      }
    },
    ["@keydown.left.stop"]() {
      return this.closeSub();
    }
  },
  menuItem: {
    ["@click"]() {
      this.closeSub();
      this.$data.close();
    },
    ["@mouseover"]() {
      return this.$focus.focus(this.$el);
    },
    [":tabindex"]() {
      (this.subOpen || this.subPreview) && this.$el.isEqualNode(this.$root.querySelectorAll("button")[2]) ? 0 : -1;
    },
    ["@focus"]() {
      this.$el.setAttribute("tabindex", 0);
    },
    ["@focusout"]() {
      this.$el.setAttribute("tabindex", -1);
    },
    ["@keydown.tab"]() {
      this.closeSub();
    }
  },
  open() {
    this.subOpen = true;
  },
  closeSub() {
    this.subOpen = false;
  },
  toggle() {
    this.subOpen == true ? this.closeSub() : this.open();
  },
  openPreview() {
    if (window.innerWidth <= 640) {
      return;
    }
    this.subPreview = true;
  },
  closePreview() {
    this.subPreview = false;
  }
});

// js/popover.js
var popover_default = () => ({
  popover: false,
  root: {
    ["x-id"]() {
      return ["popover"];
    }
  },
  trigger: {
    ["@click"]() {
      return this.toggle();
    },
    [":id"]() {
      return this.$id("popover") + "-trigger";
    },
    [":aria-controls"]() {
      return this.$id("popover") + "-content";
    },
    ["@keydown.esc.window"]() {
      return this.close();
    }
  },
  content: {
    ["@click.outside.capture"]() {
      if (!this.$refs.trigger.contains(this.$event.target)) {
        return this.close();
      }
    },
    ["x-anchor.offset.4"]() {
      return this.$refs.trigger;
    },
    ["x-trap"]() {
      return this.popover;
    },
    ["x-show"]() {
      return this.popover;
    },
    ["x-transition"]() {
      return true;
    },
    [":id"]() {
      return this.$id("popover") + "-content";
    },
    [":aria-labelledby"]() {
      return this.$id("popover-menu") + "-trigger";
    }
  },
  close() {
    this.popover = false;
  },
  open() {
    this.popover = true;
  },
  toggle() {
    this.popover == true ? this.close() : this.open();
  }
});

// js/select.js
var select_default = (multiple, disabled) => ({
  options: [],
  selected: [],
  selectedValues: [],
  multiple,
  disabled,
  show: false,
  root: {
    ["x-on:keydown.tab"]() {
      return this.close();
    },
    ["@click.outside.capture"]() {
      return this.close();
    },
    ["x-on:keydown.escape"]() {
      return this.close();
    }
  },
  trigger: {
    ["@click"]() {
      return this.toggle();
    },
    ["@keypress.enter"]() {
      return this.open();
    },
    [":disabled"]() {
      return this.disabled;
    }
  },
  optionList: {
    ["x-show.transition.scale.origin.top"]() {
      return this.show;
    },
    ["x-trap.noscroll"]() {
      return this.show;
    },
    ["x-anchor"]() {
      return this.$refs.select;
    },
    ["x-on:keydown.up.prevent"]() {
      return this.$focus.wrap().previous();
    },
    ["x-on:keydown.down.prevent"]() {
      return this.$focus.wrap().next();
    }
  },
  init() {
    this.loadOptions();
  },
  open() {
    if (!this.disabled) {
      this.show = true;
    }
  },
  isOpen() {
    return this.show;
  },
  close() {
    this.show = false;
  },
  toggle() {
    this.show ? this.close() : this.open();
  },
  select(index) {
    if (!!this.options[index].disabled) {
      return;
    }
    if (!this.options[index].selected || !this.multiple) {
      if (!this.multiple) {
        for (let i = 0; i < this.selected.length; i++) {
          this.options[this.selected[i]].selected = false;
        }
        this.selected.length = 0;
      }
      this.options[index].selected = true;
      this.selected.push(index);
    } else {
      this.selected.splice(this.selected.lastIndexOf(index), 1);
      this.options[index].selected = false;
    }
    this.setSelectedValues();
    this.dispatchChange();
    if (!this.multiple) {
      this.close();
    }
  },
  dispatchChange() {
    this.$nextTick(() => {
      this.$dispatch("change", { value: this.multiple ? this.selected.map((el) => this.options[el].value) : this.options[this.selected[0]].value });
    });
  },
  remove(index) {
    const idx = this.selected.indexOf(index);
    if (idx !== -1) {
      this.selected.splice(idx, 1);
      this.options[index].selected = false;
    } else {
      console.warn(`Option not found.`);
    }
    this.setSelectedValues();
    this.dispatchChange();
  },
  loadOptions() {
    const options = this.$root.childNodes[1].options;
    let lastSelected = 0;
    for (let i = 0; i < options.length; i++) {
      this.options.push({
        value: options[i].value,
        text: options[i].innerText,
        disabled: options[i].disabled,
        selected: options[i].getAttribute("selected") != null || i == 0 && !this.multiple ? this.selected.push(i) : false
      });
      if (!this.multiple && options[i].getAttribute("selected") != null) {
        this.options[lastSelected].selected = false;
        lastSelected = i;
      }
    }
  },
  setSelectedValues() {
    this.selectedValues = this.multiple ? this.selected.map((option) => {
      return this.options[option].value;
    }) : this.options[this.selected[0]].value;
  }
});

// js/sheet.js
var sheet_default = (side, transitionEnterStart, transitionEnterEnd, transitionLeaveStart, transitionLeaveEnd) => ({
  side,
  transitionEnterStart,
  transitionEnterEnd,
  transitionLeaveStart,
  transitionLeaveEnd,
  root: {
    ["x-show"]() {
      return this.$data["show"];
    },
    ["@click.stop"]() {
      return true;
    },
    ["x-cloak"]() {
      return true;
    },
    ["x-transition:enter"]() {
      return "transition ease-linear duration-150";
    },
    ["x-transition:enter-start"]() {
      return this.transitionEnterStart;
    },
    ["x-transition:enter-end"]() {
      return this.transitionEnterEnd;
    },
    ["x-transition:leave"]() {
      return "transition ease-linear duration-150";
    },
    ["x-transition:leave-start"]() {
      return this.transitionLeaveStart;
    },
    ["x-transition:leave-end"]() {
      return this.transitionLeaveEnd;
    }
  }
});

// js/switchInput.js
var switchInput_default = (disabled) => ({
  switchOn: false,
  disabled,
  root: {
    [":aria-checked"]() {
      return this.switchOn;
    },
    [":aria-labelledby"]() {
      if (this.$refs.input?.labels[0]?.id ?? false) {
        return this.$refs.input.labels[0].id;
      }
    },
    [":aria-label"]() {
      if (this.$refs.input?.labels[0].innerText ?? false) {
        return this.$refs.input.labels[0].innerText;
      }
    }
  },
  input: {
    ["x-model.boolean"]() {
      return "switchOn";
    },
    ["x-ref"]() {
      return "input";
    },
    [":disabled"]() {
      return this.disabled;
    }
  },
  trigger: {
    ["@click"]() {
      return this.toggle();
    },
    ["x-cloak"]() {
      return true;
    }
  },
  setSwitchState(value) {
    if (this.disabled) {
      return;
    }
    this.switchOn = value;
    this.$refs.input.checked = value;
    this.$dispatch("checkedChange");
  },
  toggle() {
    this.setSwitchState(!this.switchOn);
  }
});

// js/tabs.js
var tabs_default = (defaultValue, activationMode) => ({
  active: defaultValue,
  activationMode,
  tabsList: {
    ["x-id"]() {
      return ["tab"];
    },
    ["x-on:keydown.left.prevent"]() {
      return this.$focus.wrap().previous();
    },
    ["x-on:keydown.right.prevent"]() {
      return this.$focus.wrap().next();
    }
  }
});

// js/tabsContent.js
var tabsContent_default = (value) => ({
  value,
  root: {
    ["x-show"]() {
      return this.value == this.$data.active;
    },
    [":tabindex"]() {
      return this.$data.active == this.value ? 0 : -1;
    },
    ["x-cloak"]() {
      return this.value == this.$data.active;
    },
    [":aria-controls"]() {
      return this.$id("tab") + "-" + this.value + "-trigger";
    },
    [":id"]() {
      return this.$id("accordion-item") + "-panel";
    }
  }
});

// js/tabsTrigger.js
var tabsTrigger_default = (value) => ({
  value,
  root: {
    ["@click"]() {
      return this.setAsActive();
    },
    ["@focus"]() {
      if (this.$data.activationMode != "manual") {
        this.setAsActive();
      }
    },
    [":aria-selected"]() {
      return this.value == this.$data.active;
    },
    [":tabindex"]() {
      return this.$data.active == this.value ? 0 : -1;
    },
    [":class"]() {
      return { "bg-background text-foreground shadow-sm": this.$data.active == this.value };
    },
    [":aria-labelledby"]() {
      return this.$id("tab") + "-" + this.value + "-panel";
    },
    [":id"]() {
      return this.$id("accordion-item") + "-trigger";
    }
  },
  setAsActive() {
    this.$data.active = this.value;
  }
});

// js/cotton-ui.js
document.addEventListener("alpine:init", () => {
  Alpine.data("accordion", accordion_default);
  Alpine.data("accordionItem", accordionItem_default);
  Alpine.data("alert", alert_default);
  Alpine.data("avatar", avatar_default);
  Alpine.data("banner", banner_default);
  Alpine.data("calendar", calendar_default);
  Alpine.data("command", command_default);
  Alpine.data("datePicker", datePicker_default);
  Alpine.data("dialog", dialog_default);
  Alpine.data("dropdownMenu", dropdownMenu_default);
  Alpine.data("dropdownMenuSub", dropdownMenuSub_default);
  Alpine.data("popover", popover_default);
  Alpine.data("select", select_default);
  Alpine.data("sheet", sheet_default);
  Alpine.data("switchInput", switchInput_default);
  Alpine.data("tabs", tabs_default);
  Alpine.data("tabsTrigger", tabsTrigger_default);
  Alpine.data("tabsContent", tabsContent_default);
});
