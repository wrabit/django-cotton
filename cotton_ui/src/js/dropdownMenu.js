export default () => ({
    dropdownMenu: false,
    root: {
        ['x-id']() {
            return ['dropdown-menu'];
        },
        ['@click.outside.capture']() {
            //dont close when event is from content and trigger, especially when teleported
            if (!this.$refs.content.contains(this.$event.target) && !this.$refs.trigger.contains(this.$event.target)) {
                return this.close();
            }
        },
    },
    trigger: {
        ['@click']() {
            return this.toggle();
        },
        ['@keydown.down.prevent']() {
            if (!this.$refs.content.contains(document.activeElement)) {
                return this.$focus.focus(this.$refs.content.querySelector('button') ?? null)
            }
            return this.$focus.within(this.$refs.content).wrap().next();
        },
        ['@keydown.up.prevent']() {
            if (!this.$refs.content.contains(document.activeElement)) {
                return this.$focus.focus([...this.$refs.content.querySelectorAll('button')].pop() || null)
            }
            return this.$focus.within(this.$refs.content).wrap().previous();
        },
        ['@keydown']($event) {
            if ($event.key == 'Home') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus(this.$refs.content.querySelector('button') ?? null)
                }
                return this.$focus.within(this.$refs.content).wrap().first();
            }
            if ($event.key == 'End') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus([...this.$refs.content.querySelectorAll('button')].pop() || null)
                }
                return this.$focus.within(this.$refs.content).wrap().last();
            }
        },
        [':id']() {
            return this.$id('dropdown-menu') + '-trigger';
        },
        [':aria-controls']() {
            return this.$id('dropdown-menu') + '-content';
        },
        ['@keydown.esc.window']() {
            return this.close();
        },
    },
    content: {
        ['x-anchor.offset.4']() {
            return this.$refs.trigger;
        },
        ['@keydown.down.prevent']() {
            if (!this.$refs.content.contains(document.activeElement)) {
                return this.$focus.focus(this.$refs.content.querySelector('button') ?? null)
            }
            return this.$focus.within(this.$refs.content).wrap().next();
        },
        ['@keydown.up.prevent']() {
            if (!this.$refs.content.contains(document.activeElement)) {
                return this.$focus.focus([...this.$refs.content.querySelectorAll('button')].pop() || null)
            }
            return this.$focus.within(this.$refs.content).wrap().previous();
        },
        ['@keydown']($event) {
            if ($event.key == 'Home') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus(this.$refs.content.querySelector('button') ?? null)
                }
                return this.$focus.within(this.$refs.content).wrap().first();
            }
            if ($event.key == 'End') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus([...this.$refs.content.querySelectorAll('button')].pop() || null)
                }
                return this.$focus.within(this.$refs.content).wrap().last();
            }
        },
        [':id']() {
            return this.$id('dropdown-menu') + '-content';
        },
        [':aria-labelledby']() {
            return this.$id('dropdown-menu') + '-trigger';
        },
        ['x-trap.noscroll.noautofocus']() {
            return this.dropdownMenu;
        },
        ['x-show']() {
            return this.dropdownMenu;
        },
        ['x-transition']() {
            return true;
        },
    },
    menuItem: {
        ['@click']() {
            return this.close();
        },
        ['@mouseover']() {
            return this.$focus.focus(this.$el);
        },
        ['@focus']() {
            this.$el.setAttribute('tabindex', 0)
        },
        ['@focusout']() {
            this.$el.setAttribute('tabindex', -1)
        },
        ['@keydown.tab']() {
            this.close()
        },
    },
    close() {
        this.dropdownMenu = false;
    },
    open() {
        this.dropdownMenu = true;
    },
    toggle() {
        this.dropdownMenu ? this.close() : this.open()
    }

})
