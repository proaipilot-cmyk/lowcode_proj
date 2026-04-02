"""Page object for login_page."""
from pages.base_page import BasePage

class LoginPage(BasePage):
    URL_PATTERN = "*/pulse/S3/login"

    def __init__(self, page):
        super().__init__(page)
        self.requestverificationtoken = self.page.locator("[name='__RequestVerificationToken']")
        self.here = self.page.get_by_text("here.")
        self.enter_your_email = self.page.get_by_placeholder("Enter your email")
        self.preventautopass = self.page.locator("#preventAutoPass")
        self.enter_your_password = self.page.get_by_placeholder("Enter your password")
        self.redirecturl = self.page.locator("#RedirectUrl")
        self.rememberme = self.page.locator("#RememberMe")
        self.remembermedummy = self.page.locator("#RememberMeDummy")
        self.proceed = self.page.locator("#proceed")
        self.flagfield = self.page.locator("#flagfield")
        self.forgot_password = self.page.get_by_text("Forgot Password")
        self.re_enter_your_email = self.page.get_by_placeholder("Re-enter your email")
        self.app = self.page.locator("#appforgotPassword")
        self.requestedurl = self.page.locator("#requestedUrlforgotPassword")
        self.company = self.page.locator("#companyforgotPassword")
        self.back_to_login = self.page.get_by_text("Back to Login")
        self.privacy_policy = self.page.get_by_text("Privacy Policy")
        self.cookie_notice = self.page.get_by_text("Cookie Notice")
        self.accept_recommended_btn_handler = self.page.locator("#accept-recommended-btn-handler")
        self.vendor_details_button_opens_vendor_list_menu = self.page.get_by_label("Vendor Details button opens Vendor List menu")
        self.back = self.page.get_by_label("Back")
        self.vendor_search_handler = self.page.locator("#vendor-search-handler")
        self.filter = self.page.get_by_label("Filter")
        self.clear_filters_handler = self.page.locator("#clear-filters-handler")
        self.chkbox_id = self.page.locator("#chkbox-id")
        self.filter_apply_handler = self.page.locator("#filter-apply-handler")
        self.filter_cancel_handler = self.page.locator("#filter-cancel-handler")
        self.select_all_hosts_groups_handler = self.page.locator("#select-all-hosts-groups-handler")
        self.select_all_vendor_groups_handler = self.page.locator("#select-all-vendor-groups-handler")
        self.select_all_vendor_leg_handler = self.page.locator("#select-all-vendor-leg-handler")
        self.select_and_proceed = self.page.get_by_text("Select and proceed")
        self.powered_by_onetrust_opens_in_a_new_tab = self.page.get_by_label("Powered by OneTrust Opens in a new Tab")
        self.onetrust_accept_btn_handler = self.page.locator("#onetrust-accept-btn-handler")
        self.username = self.page.get_by_placeholder("Enter your email")
        self.log_in = self.page.get_by_role("button", name="Log in")

    def click_requestverificationtoken(self):
        self.requestverificationtoken.click()
        return self

    def click_here(self):
        self.here.click()
        return self

    def fill_enter_your_email(self, value: str):
        self.enter_your_email.fill(value)
        return self

    def fill_preventautopass(self, value: str):
        self.preventautopass.fill(value)
        return self

    def fill_enter_your_password(self, value: str):
        self.enter_your_password.fill(value)
        return self

    def click_redirecturl(self):
        self.redirecturl.click()
        return self

    def click_rememberme(self):
        self.rememberme.click()
        return self

    def toggle_remembermedummy(self):
        self.remembermedummy.click()
        return self

    def click_proceed(self):
        self.proceed.click()
        return self

    def click_flagfield(self):
        self.flagfield.click()
        return self

    def click_forgot_password(self):
        self.forgot_password.click()
        return self

    def fill_re_enter_your_email(self, value: str):
        self.re_enter_your_email.fill(value)
        return self

    def click_app(self):
        self.app.click()
        return self

    def click_requestedurl(self):
        self.requestedurl.click()
        return self

    def click_company(self):
        self.company.click()
        return self

    def click_back_to_login(self):
        self.back_to_login.click()
        return self

    def click_privacy_policy(self):
        self.privacy_policy.click()
        return self

    def click_cookie_notice(self):
        self.cookie_notice.click()
        return self

    def click_accept_recommended_btn_handler(self):
        self.accept_recommended_btn_handler.click()
        return self

    def click_vendor_details_button_opens_vendor_list_menu(self):
        self.vendor_details_button_opens_vendor_list_menu.click()
        return self

    def click_back(self):
        self.back.click()
        return self

    def fill_vendor_search_handler(self, value: str):
        self.vendor_search_handler.fill(value)
        return self

    def click_filter(self):
        self.filter.click()
        return self

    def click_clear_filters_handler(self):
        self.clear_filters_handler.click()
        return self

    def toggle_chkbox_id(self):
        self.chkbox_id.click()
        return self

    def click_filter_apply_handler(self):
        self.filter_apply_handler.click()
        return self

    def click_filter_cancel_handler(self):
        self.filter_cancel_handler.click()
        return self

    def toggle_select_all_hosts_groups_handler(self):
        self.select_all_hosts_groups_handler.click()
        return self

    def toggle_select_all_vendor_groups_handler(self):
        self.select_all_vendor_groups_handler.click()
        return self

    def toggle_select_all_vendor_leg_handler(self):
        self.select_all_vendor_leg_handler.click()
        return self

    def click_select_and_proceed(self):
        self.select_and_proceed.click()
        return self

    def click_powered_by_onetrust_opens_in_a_new_tab(self):
        self.powered_by_onetrust_opens_in_a_new_tab.click()
        return self

    def click_onetrust_accept_btn_handler(self):
        self.onetrust_accept_btn_handler.click()
        return self

    def fill_username(self, value: str):
        self.username.fill(value)
        return self

    def click_log_in(self):
        self.log_in.click()
        return self

