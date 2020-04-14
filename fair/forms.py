from flask_wtf import FlaskForm
from flask_wtf.html5 import URLField
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField
from wtforms_components import DateField
from wtforms.validators import DataRequired, URL, Regexp


class ErdaImportForm(FlaskForm):
    erda_url = StringField(
        "ERDA URL, e.g: "
        "https://erda.dk/public/archives/YXJjaGl2ZS05dHRxRVU=/published-archive.html",
        validators=[
            URL(
                require_tld=False,
                message="This URL does not appear to be valid, remember the "
                "URL should start with https://erda.dk",
            )
        ],
    )


# Used to validate the ajax post search when the user is typing
class SciSearchForm(FlaskForm):
    sci_area = StringField(
        "",
        validators=[
            Regexp(
                regex=r"^[\w ]*$",
                message="Allowed characters include" " letters and spaces",
            )
        ],
    )


class TagsSearchForm(FlaskForm):
    tag = StringField(
        "Tags Search",
        validators=[
            Regexp(
                r"^[\w,:_\-* ]*$",
                message="Allowed tag characters include "
                "letters spaces and , : _ - *",
            )
        ],
    )


class FairDatasetForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    doi = StringField("DOI (Optional)")
    data_url = URLField("Data Link (Optional)", validators=[URL()])
    date = DateField("Date of publication", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    sci_area = StringField(
        "Scientific Area",
        validators=[DataRequired()],
        render_kw={"autocomplete": "off"},
    )
    references = StringField("References (Optional)", validators=[])
    image = FileField(
        "Dataset Image",
        validators=[
            FileRequired(),
            FileAllowed(["jpg", "png"], "Only JPG and PNG images are allowed"),
        ],
    )
    tags = StringField(
        "Tags",
        validators=[
            DataRequired(),
            Regexp(
                r"^[\w,:_\- ]*$",
                message="Allowed tag characters include " "letters spaces and , : _ -",
            ),
        ],
    )

    orcid = StringField(
        "ORCID (Optional)",
        validators=[
            Regexp(
                r"^(\d{4}-?){4}$|^$",
                message="The allowed format is" " 0000-0000-0000-0000 or nothing",
            )
        ],
    )


class LoginForm(FlaskForm):
    auth_provider = SelectField(
        "Authentication Provider",
        choices=[
            ("https://openid.ku.dk", "KU OpenID"),
            ("https://ext.erda.dk/openid/id/", "ERDA Login"),
            ("https://ext.idmc.dk/openid/id/", "IDMC Ext Login"),
        ],
    )
