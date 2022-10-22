from picoconstants import db_handler


def build_fake_web_page():
    """
    Load all the steps stored from the database and creates a html file with
    fake submission fields using those steps. Later, this web page can be used
    for submission testing with a local web server.
    :return:
    """
    def get_step():
        """
        Step generator
        :return:
        """
        for step_text in [step[0] for step in set(db_handler.select_filtered('ai_failed', ['text'], '')) if step]:
            yield step_text

    # Store the submission fields into a separate file.
    fields = ''
    id_num = 1
    for text in get_step():
        fields += f"""
        <div class="form-group" style="margin-bottom: 10px;">
            <h3 style="font-weight: 700; margin-bottom: 0px">{id_num}: </h3>
            <label for="proof_2" style="font-size: 18px; font-weight: 600; color: rgb(107, 107, 71); margin-bottom: 0px;">
                {text}
            </label>
            <textarea id="proof_{id_num}" maxlength="2000" cols="30" rows="4" class="form-control"></textarea>
        </div>
        """
        id_num += 1
    with open("test_fields.txt", 'w+') as f:
        f.write(fields)

    # Combine all the webpage parts and save as a html file.
    with open("test.html", 'w+') as file:
        before = open('until-submit-fields.txt', 'r').read()
        submit_fields = open("test_fields.txt", 'r').read()
        after = open("after-submit-fields.txt", 'r').read()
        file.write(f"{before}\n{submit_fields}\n{after}")
    print("Fake submission html page generated. Move the file into the active server directory.")


build_fake_web_page()
