/** @odoo-module **/

import { Component, useState, onWillUnmount } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FormView extends Component {
    static template = "app_one.formView";

    setup() {
        this.state = useState({
            name: "",
            postcode: "",
            date_availability: "",
        });

        this.rpc = useService("rpc");
    }

    async createRecord() {
        await this.rpc("/web/dataset/call_kw/", {
            model: "property",
            method: "create",
            args: [
                {
                    name: this.state.name,
                    postcode: this.state.postcode,
                    bedrooms: this.state.bedrooms,
                    description: this.state.description,
                }
            ],
            kwargs: {},
        });
    }

    cancel() {
        this.state.name = "";
        this.state.postcode = "";
        this.state.bedrooms= "";
        this.state.description= "";
    }
}