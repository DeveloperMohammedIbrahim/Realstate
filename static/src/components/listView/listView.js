/** @odoo-module **/

import {Component, useState, onWillStart, onMounted, onWillUnmount} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {FormView} from "@app_one/components/formView/formView";

const FIELDS = ["id", "name", "postcode", "bedrooms", "description"];
const POLL_INTERVAL = 3000; // بالملي ثانية

export class ListViewActions extends Component {
    static template = "app_one.listView";
    static components = {FormView}

    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            records: [],
            error: false,
            search: "",
        });

        this.snapshot = "";      // آخر بيانات وصلت كنص، لنعرف هل تغير شيء فعلاً
        this.isFetching = false; // يمنع تداخل طلبين إن تأخر الرد أكثر من 3 ثوانٍ
        this.timer = null;

        // أول تحميل يتم قبل رسم الشاشة: لا spinner ولا وميض لرسالة "No properties"
        onWillStart(() => this.loadRecords());

        // التحديث الدوري صامت. يتوقف عندما تكون التبويبة مخفية
        onMounted(() => {
            this.timer = setInterval(() => {
                if (!document.hidden) {
                    this.loadRecords();
                }
            }, POLL_INTERVAL);
        });

        // بدونه يستمر المؤقت في الطلب بعد مغادرة الشاشة (تسريب)
        onWillUnmount(() => clearInterval(this.timer));
    }

    get filteredRecords() {
        const q = this.state.search.trim().toLowerCase();
        if (!q) {
            return this.state.records;
        }
        return this.state.records.filter((rec) =>
            [rec.name, rec.postcode, rec.description].some((v) =>
                String(v || "").toLowerCase().includes(q)
            )
        );
    }

    async loadRecords() {
        if (this.isFetching) {
            return;
        }
        this.isFetching = true;
        try {
            const records = await this.rpc("/web/dataset/call_kw", {
                model: "property",
                method: "search_read",
                args: [[]],
                kwargs: {fields: FIELDS, order: "id asc"},
            });

            // لا نلمس الـ state إلا إذا تغيرت البيانات فعلاً، فلا تُعاد الرسم بلا داعٍ
            const snapshot = JSON.stringify(records);
            if (snapshot !== this.snapshot) {
                this.snapshot = snapshot;
                this.state.records = records;
            }
            if (this.state.error) {
                this.state.error = false;
            }
        } catch (error) {
            console.error("app_one: failed to load properties", error);
            // فشل تحديث في الخلفية لا يمسح الجدول. شاشة الخطأ فقط إن لم توجد بيانات أصلاً
            if (!this.state.records.length) {
                this.state.error = true;
            }
        } finally {
            this.isFetching = false;
        }
    }

    async creatRecord() {
        await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "create",
            args: [{
                name: "creat po 3", postcode: "p0019", bedrooms: "6", description: "create record by js 4"
            }],
            kwargs: {},
        });
        this.loadRecords();
    }

    async deleteRecord(recordId) {
        await this.rpc("/web/dataset/call_kw", {
            model: "property",
            method: "unlink",
            args: [recordId],
            kwargs: {},
        });
        this.loadRecords();
    }

    toggleCreateForm() {
        this.state.showCreateForm = !this.state.showCreateForm;

    }
}

registry.category("actions").add("app_one.list_view_action", ListViewActions);