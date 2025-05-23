# Generated by Django 4.2.20 on 2025-03-27 14:15

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailcore", "0094_alter_page_locale"),
        ("cms", "0011_cmsstreampage_show_title"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("author", models.CharField(default="Philly Bike Action", max_length=128)),
                ("date", models.DateField()),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            ("card", 4),
                            ("paragraph", 6),
                            ("html", 7),
                            ("table", 8),
                            ("newsletter_signup", 9),
                        ],
                        block_lookup={
                            0: ("wagtail.images.blocks.ImageBlock", [], {}),
                            1: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {"choices": [("left", "Left"), ("right", "Right")]},
                            ),
                            2: ("wagtail.blocks.CharBlock", (), {"required": False}),
                            3: ("wagtail.blocks.RichTextBlock", (), {}),
                            4: (
                                "wagtail.blocks.StructBlock",
                                [[("image", 0), ("image_side", 1), ("header", 2), ("text", 3)]],
                                {
                                    "features": [
                                        "anchor-identifier",
                                        "h2",
                                        "h3",
                                        "h4",
                                        "bold",
                                        "italic",
                                        "ol",
                                        "ul",
                                        "hr",
                                        "link",
                                        "document-link",
                                        "image",
                                        "embed",
                                        "code",
                                        "blockquote",
                                    ]
                                },
                            ),
                            5: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "choices": [
                                        ("left", "Left"),
                                        ("center", "Center"),
                                        ("right", "Right"),
                                    ]
                                },
                            ),
                            6: (
                                "wagtail.blocks.StructBlock",
                                [[("alignment", 5), ("paragraph", 3)]],
                                {
                                    "features": [
                                        "anchor-identifier",
                                        "h2",
                                        "h3",
                                        "h4",
                                        "bold",
                                        "italic",
                                        "ol",
                                        "ul",
                                        "hr",
                                        "link",
                                        "document-link",
                                        "image",
                                        "embed",
                                        "code",
                                        "blockquote",
                                    ]
                                },
                            ),
                            7: ("wagtail.blocks.RawHTMLBlock", (), {}),
                            8: (
                                "wagtail.contrib.table_block.blocks.TableBlock",
                                (),
                                {
                                    "table_options": {
                                        "contextMenu": [
                                            "row_above",
                                            "row_below",
                                            "---------",
                                            "col_left",
                                            "col_right",
                                            "---------",
                                            "remove_row",
                                            "remove_col",
                                            "---------",
                                            "undo",
                                            "redo",
                                            "---------",
                                            "copy",
                                            "cut",
                                            "---------",
                                            "alignment",
                                        ],
                                        "editor": "text",
                                        "renderer": "html",
                                    }
                                },
                            ),
                            9: ("wagtail.blocks.StructBlock", [[]], {}),
                        },
                    ),
                ),
            ],
            options={
                "verbose_name": "Post",
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="PostsContainerPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "verbose_name": "Posts",
            },
            bases=("wagtailcore.page",),
        ),
    ]
