
# Moodle Multi-Announcement Automation Script

This project automates posting announcements to multiple Moodle forums using Selenium. It also supports uploading attachments if present and handles login via Microsoft 365 SSO.

## Features

- Automatically posts announcements to multiple Moodle courses.
- Supports file attachments.
- Handles Microsoft 365 SSO login.
- Waits for overlays (lightboxes) and ensures proper element interaction.
- Logs all actions to help troubleshoot any issues.

## Prerequisites

1. **Google Chrome**: Ensure you have the latest version of Chrome installed.
2. **ChromeDriver**: The version of ChromeDriver should match the version of Chrome installed. Download it from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).
3. **Python**: Ensure you have Python installed (version 3.x). You can download it from [here](https://www.python.org/downloads/).

## Installation

1. **Clone this repository** to your local machine:

   ```bash
   git clone https://github.com/Yusufathi/moodle_multi_annoucement_make.git
   ```

2. **Install the required Python packages**:

   ```bash
   pip install selenium
   ```

3. **Place the ChromeDriver in the root directory** of your project (next to the script).

4. **Project Folder Structure**:

   ```
   project-root/
   ├── chromedriver.exe
   ├── moodle_multi_announcement_log.txt
   ├── input/
   │   ├── links.txt           # File containing the Moodle forum links.
   │   ├── subject.txt         # File containing the subject of the announcement.
   │   ├── message.txt         # File containing the message body of the announcement.
   │   └── attachments/        # Folder containing files to be attached (optional).
   └── main.py
   ```

## Input Files

1. **`links.txt`**: Contains the URLs of the Moodle forums where announcements will be posted. Each URL should be on a new line.

2. **`subject.txt`**: The subject/title of the announcement.

3. **`message.txt`**: The body content of the announcement.

4. **`attachments/` folder**: Contains any files that need to be attached with the announcement. This folder can be empty if no attachments are needed.

## How to Use

1. **Prepare Input Files**:
   - Fill `input/links.txt` with the Moodle forum URLs.
   - Write the subject and message for your announcement in `input/subject.txt` and `input/message.txt`.
   - Place any files you want to attach inside the `input/attachments/` folder.

2. **Run the Script**:

   Open your terminal or command prompt, navigate to the project root, and run:

   ```bash
   python main.py
   ```

3. **Login to Moodle**:
   - Once the script opens the browser, log in to Moodle using your Microsoft 365 credentials manually.
   - After logging in, go back to the terminal and press **Enter** to continue.

4. **Automatic Posting**:
   - The script will loop through each forum link in `links.txt` and post the announcement.
   - If there are attachments, it will upload the files and submit the post.
   - Once finished, the browser will close automatically.

## Logs

All actions are logged in `moodle_multi_announcement_log.txt`. This includes any errors or issues encountered during the process.

## Example

Here’s an example of what the `links.txt`, `subject.txt`, and `message.txt` might look like:

### `input/links.txt`

```
https://moodle.nu.edu.eg/mod/forum/view.php?id=123456
https://moodle.nu.edu.eg/mod/forum/view.php?id=789012
```

### `input/subject.txt`

```
Important Update on Homework Submission
```

### `input/message.txt`

```
Dear Students,

Please note that the deadline for the homework submission has been extended to Friday, October 15th. Make sure to submit all assignments before the new deadline.

Best regards,
Your Instructor
```

### Attachments

Simply place the files you want to attach in the `input/attachments/` folder. The script will automatically detect and upload them with the announcement.

## Troubleshooting

- **Path is not absolute**: Make sure all file paths are absolute. The script automatically converts relative paths, but ensure your directory structure is correct.
- **Element not clickable**: This usually happens when an overlay or modal is blocking the element. The script waits for the overlay to disappear, but if issues persist, adjust the waiting times (`time.sleep()`) or use `WebDriverWait`.
- **Matching ChromeDriver**: Ensure your ChromeDriver version matches your installed Chrome version. If the versions mismatch, download the correct version from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).

## License

This project is open-source and free to use under the MIT License.
