export default (value) => ({
    keyword: value,
    focusedItem: null,
    root: {
        ['@keydown']($event) {
            if ($event.key == 'Home') {
                this.selectOption(1, false)
            }
            if ($event.key == 'End') {
                this.selectOption(-1, false)
            }
        },
        ['@keydown.capture.down.prevent']() {
            this.selectOption(1)
        },
        ['@keydown.capture.up.prevent']() {
            this.selectOption(-1)
        },
        ['@keydown.capture.enter.prevent']() {
            if (this.focusedItem != null) {
                this.focusedItem.click()
            }
        },
    },
    init() {
        this.$nextTick(() => {
            this.selectOption(0, false)
        })
    },
    commandInput: {
        ['@input']() {
            this.keyword = this.$el.value;
            this.$nextTick(() => {
                this.selectOption(0, false)
            })
            this.$dispatch("valueChange", { value: this.keyword });
        },
        [':id']() {
            return this.$id('command') + '-input';
        },
        [':aria-controls']() {
            return this.$id('command') + '-list';
        },
    },
    commandList: {
        [':id']() {
            return this.$id('command') + '-list';
        },
    },
    commandItem: {
        [':data-cmd-item']() {
            return true;
        },
        [':data-selected']() {
            return this.$el.contains(this.focusedItem);
        },
        [':aria-selected']() {
            return this.$el.contains(this.focusedItem);
        },
        [':tabindex']() {
            return this.$el.contains(this.focusedItem) ? 0 : -1;
        },
        ['x-effect']() {
            if (this.keyword == '' || this.fuzzySearch(this.keyword, this.$el.innerText)) {
                this.$el.dataset.active = true
                this.$el.style.display = "flex"
            } else {
                this.$el.dataset.active = false
                this.$el.style.display = "none"
            }
        },
        ['@mouseenter']() {
            return this.focusedItem = this.$el;
        },
    },
    commandGroupHeading: {
        [':id']() {
            return this.$id('command') + '-group-heading';
        },
    },
    commandGroup: {
        [':id']() {
            return this.$id('command') + '-group';
        },
        [':aria-labelledby']() {
            return this.$id('command') + '-group-heading';
        },
    },
    commandGroupContainer: {
        ['x-effect']() {
            this.keyword == ''; // dont delete this helps with reactivity
            this.$nextTick(() => {
                this.$el.style.display = this.$el.querySelectorAll('[data-active=true]').length > 0 ? 'block' : 'none'
            })
        },
    },
    commandEmpty: {
        ['x-effect']() {
            this.keyword == ''; // dont delete this helps with reactivity
            this.$nextTick(() => {
                this.$el.style.display = this.$refs.list.querySelectorAll('[data-active=true]').length > 0 ? 'none' : 'block'
            })
        },
    },
    selectOption(index, relative = true) {
        let nodeList = this.$refs.list.querySelectorAll("[data-active=true]");
        let nodeListArray = Array.from(nodeList);
        let initialIndex = index
        if (nodeList.length == 0 || !nodeListArray.some(node => JSON.parse(node.dataset.disabled) == false)) {
            return;
        }
        if (relative) {
            let previousIndex = Array.from(nodeList).findIndex(node => node.isEqualNode(this.focusedItem)) ?? 0;
            index += previousIndex;
        }
        index += index < 0 ? nodeList.length : 0; //make indexing work for negative numbers
        index = index % nodeList.length
        while (JSON.parse(nodeList[index].dataset.disabled)) {
            index += initialIndex < 0 ? -1 : 1 //scrolling up or down
            index = index % nodeList.length
        }
        this.focusedItem = nodeList[index];
        this.focusedItem.scrollIntoView(initialIndex < 0); //scrolling up or down
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
})
