/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { useService } from "@web/core/utils/hooks";

/**
 * نافذة (popup) واحدة للـ Create والـ Edit.
 *
 * - بدون prop اسمها `record`  → Create  (rpc: create)
 * - مع `record` فيها id        → Edit    (rpc: write)
 *
 * بتتفتح بـ dialog.add(FormView, {...}) وخدمة الـ dialog هي اللي بتحقن `close`.
 */
export class FormView extends Component {
    static template = "app_one.formView";
    static components = { Dialog };
    static props = {
        record: { type: Object, optional: true },     // السجل المراد تعديله
        onSaved: { type: Function, optional: true },  // يُنادى بعد نجاح الحفظ
        close: Function,                               // تحقنه خدمة الـ dialog
    };

    setup() {
        this.rpc = useService("rpc");

        // ننسخ القيم في state خاص بالنافذة. لو ربطنا الحقول بالـ record نفسه،
        // أول polling يجيب بيانات جديدة هيمسح اللي المستخدم كاتبه.
        const rec = this.props.record || {};
        this.state = useState({
            name: rec.name || "",
            postcode: rec.postcode || "",
            bedrooms: rec.bedrooms ?? "",
            description: rec.description || "",   // Odoo بيرجّع false للحقل الفاضي
            saving: false,
            error: "",
        });
    }

    get isEdit() {
        return Boolean(this.props.record && this.props.record.id);
    }

    get title() {
        return this.isEdit ? "Edit property" : "New property";
    }

    get values() {
        return {
            name: this.state.name.trim(),
            postcode: this.state.postcode.trim(),
            bedrooms: parseInt(this.state.bedrooms, 10) || 0,
            description: this.state.description,
        };
    }

    async save() {
        if (this.state.saving) {
            return; // ضغطة تانية أثناء الحفظ = تجاهل
        }
        if (!this.state.name.trim()) {
            this.state.error = "Name is required.";
            return;
        }
        this.state.error = "";
        this.state.saving = true;
        try {
            if (this.isEdit) {
                // write: args = [[ids], values]   (لاحظ: id جوه list)
                await this.rpc("/web/dataset/call_kw", {
                    model: "property",
                    method: "write",
                    args: [[this.props.record.id], this.values],
                    kwargs: {},
                });
            } else {
                // create: args = [values]
                await this.rpc("/web/dataset/call_kw", {
                    model: "property",
                    method: "create",
                    args: [this.values],
                    kwargs: {},
                });
            }
        } catch (error) {
            this.state.saving = false; // نخلي الزرار يشتغل تاني، وOdoo هيعرض الخطأ
            throw error;
        }
        this.props.onSaved?.();
        this.props.close();
    }

    cancel() {
        this.props.close();
    }
}