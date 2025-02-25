import accordion from './accordion.js'
import accordionItem from './accordionItem.js';
import alert from './alert.js';
import avatar from './avatar.js';
import banner from './banner.js';
import calendar from './calendar.js';
import command from './command.js';
import datePicker from './datePicker.js';
import dialog from './dialog.js';
import dropdownMenu from './dropdownMenu.js';
import dropdownMenuSub from './dropdownMenuSub.js';
import popover from './popover.js';
import select from './select.js';
import sheet from './sheet.js';
import switchInput from './switchInput.js';
import tabs from './tabs.js';
import tabsContent from './tabsContent.js';
import tabsTrigger from './tabsTrigger.js';

document.addEventListener('alpine:init', () => {
    Alpine.data('accordion', accordion)
    Alpine.data('accordionItem', accordionItem)
    Alpine.data('alert', alert)
    Alpine.data('avatar', avatar)
    Alpine.data('banner', banner)
    Alpine.data('calendar', calendar)
    Alpine.data('command', command)
    Alpine.data('datePicker', datePicker)
    Alpine.data('dialog', dialog)
    Alpine.data('dropdownMenu', dropdownMenu)
    Alpine.data('dropdownMenuSub', dropdownMenuSub)
    Alpine.data('popover', popover)
    Alpine.data('select', select)
    Alpine.data('sheet', sheet)
    Alpine.data('switchInput', switchInput)
    Alpine.data('tabs', tabs)
    Alpine.data('tabsTrigger', tabsTrigger)
    Alpine.data('tabsContent', tabsContent)
})
