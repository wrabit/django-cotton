export default () => ({
    dropdownMenu: false,
    position: 'bottom',
    align: 'start',
    offset: 4,
    responsive: false,

    init() {
        // Keep the open menu correctly placed when the viewport changes
        // (resize, or scrolling within a scroll container).
        let ticking = false;
        this._reposition = () => {
            if (!this.dropdownMenu || ticking) return;
            ticking = true;
            requestAnimationFrame(() => {
                this.positionDropdown();
                ticking = false;
            });
        };
        window.addEventListener('resize', this._reposition);
        window.addEventListener('scroll', this._reposition, true);
    },

    destroy() {
        if (!this._reposition) return;
        window.removeEventListener('resize', this._reposition);
        window.removeEventListener('scroll', this._reposition, true);
    },

    positionDropdown() {
        if (!this.$refs.content || !this.$refs.trigger) return;

        const trigger = this.$refs.trigger.getBoundingClientRect();
        const content = this.$refs.content;
        const offset = parseInt(this.offset);

        let finalPosition = this.position;
        let finalAlign = this.align;

        // Responsive positioning: detect viewport boundaries and flip if needed
        if (this.responsive) {
            const contentRect = content.getBoundingClientRect();
            const viewportWidth = window.innerWidth;
            const viewportHeight = window.innerHeight;

            // Check vertical overflow
            if (this.position === 'bottom') {
                const spaceBelow = viewportHeight - trigger.bottom - offset;
                const spaceAbove = trigger.top - offset;
                if (contentRect.height > spaceBelow && spaceAbove > spaceBelow) {
                    finalPosition = 'top';
                }
            } else if (this.position === 'top') {
                const spaceAbove = trigger.top - offset;
                const spaceBelow = viewportHeight - trigger.bottom - offset;
                if (contentRect.height > spaceAbove && spaceBelow > spaceAbove) {
                    finalPosition = 'bottom';
                }
            }

            // Check horizontal overflow
            if (this.position === 'bottom' || this.position === 'top') {
                if (this.align === 'start') {
                    const spaceRight = viewportWidth - trigger.left;
                    if (contentRect.width > spaceRight && trigger.right > contentRect.width) {
                        finalAlign = 'end';
                    }
                } else if (this.align === 'end') {
                    const spaceLeft = trigger.right;
                    if (contentRect.width > spaceLeft && (viewportWidth - trigger.left) > contentRect.width) {
                        finalAlign = 'start';
                    }
                }
            }
        }

        // Reset positioning
        content.style.top = '';
        content.style.bottom = '';
        content.style.left = '';
        content.style.right = '';
        content.style.transform = '';

        // Position based on settings (using final calculated position)
        if (finalPosition === 'bottom') {
            content.style.top = `calc(100% + ${offset}px)`;
        } else if (finalPosition === 'top') {
            content.style.bottom = `calc(100% + ${offset}px)`;
        } else if (finalPosition === 'left') {
            content.style.right = `calc(100% + ${offset}px)`;
        } else if (finalPosition === 'right') {
            content.style.left = `calc(100% + ${offset}px)`;
        }

        // Align based on settings (using final calculated alignment)
        if (finalPosition === 'top' || finalPosition === 'bottom') {
            if (finalAlign === 'start') {
                content.style.left = '0';
            } else if (finalAlign === 'end') {
                content.style.right = '0';
            } else if (finalAlign === 'center') {
                content.style.left = '50%';
                content.style.transform = 'translateX(-50%)';
            }
        } else {
            if (finalAlign === 'start') {
                content.style.top = '0';
            } else if (finalAlign === 'end') {
                content.style.bottom = '0';
            } else if (finalAlign === 'center') {
                content.style.top = '50%';
                content.style.transform = 'translateY(-50%)';
            }
        }
    },

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
                return this.$focus.focus(this.$refs.content.querySelector('button, a[role="menuitem"]') ?? null)
            }
            return this.$focus.within(this.$refs.content).wrap().next();
        },
        ['@keydown.up.prevent']() {
            if (!this.$refs.content.contains(document.activeElement)) {
                return this.$focus.focus([...this.$refs.content.querySelectorAll('button, a[role="menuitem"]')].pop() || null)
            }
            return this.$focus.within(this.$refs.content).wrap().previous();
        },
        ['@keydown']($event) {
            if ($event.key == 'Home') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus(this.$refs.content.querySelector('button, a[role="menuitem"]') ?? null)
                }
                return this.$focus.within(this.$refs.content).wrap().first();
            }
            if ($event.key == 'End') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus([...this.$refs.content.querySelectorAll('button, a[role="menuitem"]')].pop() || null)
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
        ['@keydown.down.prevent']() {
            if (!this.$refs.content.contains(document.activeElement)) {
                return this.$focus.focus(this.$refs.content.querySelector('button, a[role="menuitem"]') ?? null)
            }
            return this.$focus.within(this.$refs.content).wrap().next();
        },
        ['@keydown.up.prevent']() {
            if (!this.$refs.content.contains(document.activeElement)) {
                return this.$focus.focus([...this.$refs.content.querySelectorAll('button, a[role="menuitem"]')].pop() || null)
            }
            return this.$focus.within(this.$refs.content).wrap().previous();
        },
        ['@keydown']($event) {
            if ($event.key == 'Home') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus(this.$refs.content.querySelector('button, a[role="menuitem"]') ?? null)
                }
                return this.$focus.within(this.$refs.content).wrap().first();
            }
            if ($event.key == 'End') {
                if (!this.$refs.content.contains(document.activeElement)) {
                    return this.$focus.focus([...this.$refs.content.querySelectorAll('button, a[role="menuitem"]')].pop() || null)
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
        this.$nextTick(() => this.positionDropdown());
    },
    toggle() {
        this.dropdownMenu ? this.close() : this.open()
    }

})
