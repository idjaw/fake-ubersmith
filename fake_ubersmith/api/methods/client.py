# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fake_ubersmith.api.base import Base
from fake_ubersmith.api.ubersmith import FakeUbersmithError
from fake_ubersmith.api.utils.response import response


class Client(Base):
    def __init__(self, data_store):
        super().__init__(data_store)

        self.credit_card_response = 1
        self.credit_card_delete_response = True

    def hook_to(self, entity):
        entity.register_endpoints(
            ubersmith_method='client.cc_add',
            function=self.client_cc_add
        )
        entity.register_endpoints(
            ubersmith_method='client.cc_update',
            function=self.client_cc_update
        )
        entity.register_endpoints(
            ubersmith_method='client.cc_info',
            function=self.client_cc_info
        )
        entity.register_endpoints(
            ubersmith_method='client.cc_delete',
            function=self.client_cc_delete
        )
        entity.register_endpoints(
            ubersmith_method='client.get',
            function=self.client_get
        )
        entity.register_endpoints(
            ubersmith_method='client.add',
            function=self.client_add
        )
        entity.register_endpoints(
            ubersmith_method='client.contact_add',
            function=self.contact_add
        )
        entity.register_endpoints(
            ubersmith_method='client.contact_get',
            function=self.contact_get
        )

    def client_add(self, form_data):
        client_id = str(len(self.data_store.clients) + 1)

        client_data = form_data.copy()
        client_data["clientid"] = client_id
        client_data["contact_id"] = str(0)

        if client_data.get("uber_login"):
            client_data["login"] = client_data.get("uber_login")
            del client_data["uber_login"]

        self.logger.info("Adding client data: {}".format(client_data))

        self.data_store.clients.append(client_data)

        return response(data=client_id)

    def client_get(self, form_data):
        client_id = form_data.get("client_id") or form_data.get("user_login")
        client = next(
            (
                client.copy() for client in self.data_store.clients
                if client["clientid"] == client_id
            ),
            None
        )
        if client is not None:
            client.pop("contact_id")
            self.logger.info("client data being returned {}".format(client))
            return response(data=client)
        else:
            self.logger.info("Can't find client ID - {}".format(client_id))
            return response(
                error_code=1,
                message="Client ID '{}' not found.".format(client_id)
            )

    def contact_add(self, form_data):
        contact_id = str(len(self.data_store.contacts) + 1)

        contact_data = form_data.copy()
        contact_data["contact_id"] = contact_id
        self.data_store.contacts.append(contact_data)

        self.logger.info("Contact info added: {}".format(contact_data))

        return response(data=contact_id)

    def contact_get(self, form_data):
        if "user_login" in form_data:
            self.logger.info("Looking up contact info by user_login")
            return self._get_contact_response(
                "uber_login", 'user_login', form_data['user_login']
            )
        elif "contact_id" in form_data:
            self.logger.info("Looking up contact info by contact_id")
            return self._get_contact_response(
                "contact_id", 'contact_id', form_data['contact_id']
            )

        self.logger.error("No valid user_login or contact_id specified")
        return response(error_code=1, message="No contact ID specified")

    def client_cc_add(self, form_data):
        if isinstance(self.credit_card_response, FakeUbersmithError):
            return response(
               error_code=self.credit_card_response.code,
               message=self.credit_card_response.message
            )
        return response(data=self.credit_card_response)

    def client_cc_update(self, form_data):
        if isinstance(self.credit_card_response, FakeUbersmithError):
            return response(
               error_code=self.credit_card_response.code,
               message=self.credit_card_response.message
            )
        return response(data=True)

    def client_cc_info(self, form_data):
        # returns no error if providing parameters, only an empty list
        if "billing_info_id" in form_data:
            return response(
                data={
                    cc["billing_info_id"]: cc
                    for cc in self.data_store.credit_cards
                    if cc["billing_info_id"] == form_data["billing_info_id"]
                }
            )
        elif "client_id" in form_data:
            return response(
                data={
                    cc["billing_info_id"]: cc
                    for cc in self.data_store.credit_cards
                    if cc["clientid"] == form_data["client_id"]
                }
            )
        else:
            return response(
                error_code=1,
                message="request failed: client_id parameter not supplied"
            )

    def client_cc_delete(self, form_data):
        if isinstance(self.credit_card_delete_response, FakeUbersmithError):
            return response(
                error_code=self.credit_card_delete_response.code,
                message=self.credit_card_delete_response.message
            )
        return response(data=True)

    def _get_contact_response(self, lookup_key, matcher_key, matcher_value):
        contact = next(
            (
                contact for contact in self.data_store.contacts
                if contact[lookup_key] == matcher_value
            ),
            None
        )

        self.logger.info("Getting contact info: {}".format(contact))

        return response(data=contact) if contact else response(
            error_code=1, message="Invalid {} specified.".format(matcher_key)
        )
