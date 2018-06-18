"""Parse information from snow requests."""


class SnowVars(object):
    """Terraform to ServiceNow cariable converter."""

    def __init__(self, json_obj, cat_item_id, repo_namespace, module_version,
                 os_type, repo_url, aws_region="us-east-1",
                 org_name="plus3it-poc02"):
        """Initialize."""
        self.cat_item_id = cat_item_id
        self.cat_item_list = []
        self.json_obj = json_obj
        self.os_type = os_type
        self.counter = 0
        self.repo_namespace = repo_namespace
        self.module_version = module_version
        self.aws_region = aws_region
        self.org_name = org_name
        self.repo_url = repo_url

    def create_var(self, var_name, obj_type, q_txt, t_tip, h_txt,
                   def_val, order_val, m_toggle):
        """Create catalog item variable."""
        self.cat_item_list.append(
             {
               "name": var_name,
               "type": obj_type,
               "cat_item": self.cat_item_id,
               "question_text": q_txt,
               "tooltip": t_tip,
               "default_value": def_val,
               "help_text": h_txt,
               "order": order_val,
               "mandatory": m_toggle
               })

    def parse_tf_vars(self):
        """Convert JOSN formatted terraform vars to ServiceNow vars."""
        for var_list in self.json_obj[0]['variable']:
            for key in var_list:
                var_name = key
                mandatory_toggle = 'false'
                if var_list[key][0]['type'] == 'string':
                    obj_type = 'String'
                try:
                    def_val = var_list[key][0]['default']
                    order_val = 1000
                except KeyError as e:
                    mandatory_toggle = 'true'
                    if var_name != 'Name':
                        obj_type = 'Select Box'
                    self.counter = self.counter + 10
                    order_val = self.counter
                    def_val = ""
                desc = var_list[key][0]['description']
                self.create_var(var_name='tfv_' + var_name, obj_type=obj_type,
                                q_txt=var_name, t_tip=desc, def_val=def_val,
                                h_txt=desc, order_val=order_val,
                                m_toggle=mandatory_toggle)

    def create_adv_toggle(self):
        """Create the advanced mode toggle."""
        # requires json_to_servicenow run first in order update the counter to
        # match the number of required vars
        self.counter = self.counter + 10
        self.create_var(var_name='adv_toggle',
                        obj_type="CheckBox",
                        q_txt="Show Advanced Options",
                        t_tip="Select to show advanced options",
                        def_val="",
                        h_txt="",
                        order_val=self.counter,
                        m_toggle="false")

    def create_role_var(self):
        """Create the role variable."""
        # different from gen_aws_role - defines values of 'child' vars
        self.create_var(var_name='Roles',
                        obj_type="Select Box",
                        q_txt="AWS role(s)",
                        t_tip="AWS role(s)",
                        def_val="",
                        h_txt="AWS role(s)",
                        order_val=1,
                        m_toggle="false")

    def create_os_type_var(self):
        """Create the os type variable."""
        self.create_var(var_name='gen_OS_Type',
                        obj_type="String",
                        q_txt="OS Type",
                        t_tip="OS Type",
                        def_val=self.os_type,
                        h_txt="OS Type",
                        order_val=1000,
                        m_toggle="false")

    def create_gen_aws_role(self):
        """Create the aws role vairable."""
        self.create_var(var_name='gen_aws_role',
                        obj_type="String",
                        q_txt="AWS role to assume",
                        t_tip="AWS role to assume",
                        def_val="NONE",
                        h_txt="AWS role to assume",
                        order_val=1000,
                        m_toggle="false")

    def create_gen_aws_account_info(self):
        """Create the aws role vairable."""
        self.create_var(var_name='gen_AwsAccountInfo',
                        obj_type="Multi Line Text",
                        q_txt="AWS account info",
                        t_tip="AWS account info",
                        def_val="NONE",
                        h_txt="AWS account info",
                        order_val=1000,
                        m_toggle="false")

    def create_gen_repo_namespace(self):
        """Create the repo_namespace variable."""
        # aka repo_id
        self.create_var(var_name='gen_repo_namespace',
                        obj_type="String",
                        q_txt="Gitlab repo namespace",
                        t_tip="Gitlab repo namespace",
                        def_val=self.repo_namespace,
                        h_txt="Gitlab repo namespace where this module is"
                              + "maintained",
                        order_val=1000,
                        m_toggle="false")

    def create_gen_module_version(self):
        """Crete the gen_module_version variable."""
        # aka repo_version
        self.create_var(var_name='gen_module_version',
                        obj_type="String",
                        q_txt="Terraform module version number",
                        t_tip="Terraform module version number",
                        def_val=self.module_version,
                        h_txt="Terraform module version number",
                        order_val=1000,
                        m_toggle="false")

    def create_gen_region(self):
        """Crete the gen_region variable."""
        self.create_var(var_name='gen_region',
                        obj_type="String",
                        q_txt="Target AWS region",
                        t_tip="Target AWS region",
                        def_val=self.aws_region,
                        h_txt="Target AWS region",
                        order_val=1000,
                        m_toggle="false")

    def create_gen_org_name(self):
        """Crete the gen_org_name variable."""
        self.create_var(var_name='gen_org_name',
                        obj_type="String",
                        q_txt="TFE organization name",
                        t_tip="TFE organization name",
                        def_val=self.org_name,
                        h_txt="TFE organization name",
                        order_val=1000,
                        m_toggle="false")

    def create_gen_repo_url(self):
        """Crete the gen_org_name variable."""
        self.create_var(var_name='gen_repo_url',
                        obj_type="String",
                        q_txt="Gitlab repo url",
                        t_tip="Gitlab repo url",
                        def_val=self.repo_url,
                        h_txt="Gitlab repo url",
                        order_val=1000,
                        m_toggle="false")

    def get_vars(self):
        """Preform correct order of operations and return variables."""
        self.parse_tf_vars()
        self.create_adv_toggle()
        self.create_gen_aws_role()
        self.create_gen_aws_account_info()
        self.create_gen_repo_namespace()
        self.create_gen_module_version()
        self.create_gen_region()
        self.create_gen_org_name()
        self.create_os_type_var()
        self.create_gen_repo_url()

        self.create_role_var()
        return self.cat_item_list
