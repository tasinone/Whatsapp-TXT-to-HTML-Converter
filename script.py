import re
from datetime import datetime
import os

# HTML templates remain the same as before, adding new ones for additional message types
encryption_notice_template = """
<div class='encryption-notice'>
    <i class='fas fa-lock'></i> {date}, {time} - Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them. Tap to learn more.
</div>
"""

call_notification_template = """
<div class='call-notification'>
    <i class='fas fa-phone call-icon'></i>
    <span>{call_type} audio call</span>
    <span class='timestamp'>{timestamp}</span>
</div>
"""

incoming_message_template = """
<div class='message receiver'>
    {message_text}
    <span class='timestamp'>{timestamp}</span>
</div>
"""

outgoing_message_template = """
<div class='message sender'>
    {message_text}
    <span class='timestamp'>{timestamp} <i class="fas fa-check-double" style="color: #4fc3f7;"></i></span>
</div>
"""

date_header_template = """
<div class='dates'>
    <span>{formatted_date}</span>
</div>
"""

single_image_template = """
<div class='message {message_class}'>
    <div class='media-container'>
        <img src='{image_path}' alt='Shared image' class='attachment' onclick="openLightbox(this.src)">
    </div>
    {caption_html}
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

image_grid_template = """
<div class='message {message_class}'>
    <div class='image-grid'>
        {image_elements}
    </div>
    {caption_html}
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

voice_message_template = """
<div class='message {message_class}'>
    <div class='audio-message'>
        <img src='media/{avatar_image}' alt='Sender Avatar' class='audio-avatar'>
        <div class='audio-controls'>
            <div class='play-button' onclick="toggleAudio(this)">
                <i class='fas fa-play'></i>
            </div>
            <div class='progress-bar' onclick="seekAudio(event, this)">
                <div class='progress'></div>
            </div>
            <span class='audio-time'>0:00</span>
        </div>
        <audio src="{audio_path}" style="display: none;"></audio>
    </div>
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

video_template = """
<div class='message {message_class}'>
    <div class='media-container'>
        <video class='attachment' onclick="openLightbox(this.querySelector('source').src)">
            <source src='{video_path}' type='video/mp4'>
            Your browser does not support the video tag.
        </video>
    </div>
    {caption_html}
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

video_grid_template = """
<div class='message {message_class}'>
    <div class='image-grid'>
        {video_elements}
    </div>
    {caption_html}
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

audio_message_template = """
<div class='message {message_class}'>
    <div class='audio-message'>
        <div class='audio-controls'>
            <div class='play-button' onclick="toggleAudio(this)">
                <i class='fas fa-play'></i>
            </div>
            <div class='progress-bar' onclick="seekAudio(event, this)">
                <div class='progress'></div>
            </div>
            <span class='audio-time'>0:00</span>
        </div>
        <i class='fas fa-headphones-alt' style='color: #ffffff; font-size: 22px; background: orange; padding: 18px; border-radius: 50%;'></i>
        <audio src="{audio_path}" style="display: none;"></audio>
    </div>
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

document_template = """
<div class='message {message_class}'>
    <div class='file-attachment'>
        <i class='{icon_class} file-icon'></i>
        <div class='file-info'>
            <div class='file-name'>{filename}</div>
            <div class='file-meta'>{file_type} • {file_size}</div>
        </div>
    </div>
    {caption_html}
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

location_template = """
<div class='message {message_class}'>
    <div class='location-message' onclick="window.open('{map_url}')">
        <div class='location-preview'>
            <i class='fas fa-map-marker-alt' style='font-size: 24px; color: #075e54;'></i>
        </div>
        <div class='location-details'>
            <i class='fas fa-map-marker-alt'></i> Location
        </div>
    </div>
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

contact_template = """
<div class='message {message_class}'>
    <div class='contact-card'>
        <img src='media/avatar.jpg' alt='Contact Avatar' class='contact-avatar'>
        <div class='contact-info'>
            <div class='contact-name'>{contact_name}</div>
            <div class='contact-type'>{contact_type}</div>
        </div>
    </div>
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

deleted_message_template = """
<div class='message {message_class}'>
    <span class='deleted-message'>
        <i class='fas fa-ban'></i> {deleted_text}
    </span>
    <span class='timestamp'>{timestamp}{read_receipt}</span>
</div>
"""

# File type to icon mapping
FILE_ICONS = {
    'txt': 'fas fa-file-lines',
    'zip': 'fas fa-file-archive',
    'jpg': 'fas fa-file-image',
    'jpeg': 'fas fa-file-image',
    'png': 'fas fa-file-image',
    'doc': 'fas fa-file-word',
    'docx': 'fas fa-file-word',
    'xlsx': 'fas fa-file-excel',
    'pptx': 'fas fa-file-powerpoint',
    'mp3': 'fas fa-file-audio',
    'mp4': 'fas fa-file-video',
    'wav': 'fas fa-file-audio',
    'apk': 'fab fa-android',
    'pdf': 'fas fa-file-pdf',
    'webp': 'fas fa-file-image',
    'rar': 'fas fa-file-archive',
    'odt': 'fas fa-file-alt',
    'rtf': 'fas fa-file-alt',
    # Add more mappings for other file types
}

def try_parse_date(date_str):
    """
    Try to parse date string in multiple formats.
    Returns tuple of (parsed_date, format_used) or (None, None) if parsing fails
    """
    date_formats = [
        # American format
        ("%m/%d/%y", "US"),
        ("%m/%d/%Y", "US"),
        # European/International format
        ("%d/%m/%y", "EU"),
        ("%d/%m/%Y", "EU")
    ]
    
    for date_format, format_type in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, date_format)
            return parsed_date, format_type
        except ValueError:
            continue
    return None, None

def get_other_person_name(lines, user_name):
    """Extract the other person's name from the chat"""
    for line in lines:
        # Updated regex to be more flexible with date formats
        match = re.match(r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2} - (.*?):", line)
        if match:
            name = match.group(1).strip()
            if name != user_name:
                return name
    return "Unknown"

def is_new_message(line):
    """Check if a line starts a new message"""
    return bool(re.match(r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2} - .*?:", line))

def is_attachment(message):
    return "(file attached)" in message

def is_image(filename):
    return any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])

def is_voice_message(filename):
    return filename.lower().endswith('.opus')

def is_url(text):
    url_pattern = r'https?://\S+'
    return bool(re.match(url_pattern, text))

def format_message_text(text):
    # Convert URLs to clickable links
    url_pattern = r'(https?://\S+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

def collect_full_message(lines, start_idx):
    """Enhanced collect_full_message with better date handling"""
    message_lines = []
    i = start_idx
    
    first_line = lines[i].strip()
    match = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[APMapm]{2}) - (.*?): (.*)", first_line)
    if not match:
        return [], "", "", "", 1
    
    date_str, time, sender, message = match.groups()
    message_lines.append(message)
    
    i += 1
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            message_lines.append('')
            i += 1
            continue
        
        if is_new_message(line):
            break
            
        message_lines.append(line)
        i += 1
    
    return message_lines, date_str, time, sender, i - start_idx

def is_consecutive_image_start(lines, current_idx):
    """Check if this is the start of consecutive images"""
    if current_idx + 1 >= len(lines):
        return False
    next_line = lines[current_idx + 1].strip()
    if not is_new_message(next_line):
        return False
    match = re.match(r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2} - .*?: (.*)", next_line)
    return match and is_attachment(match.group(1)) and is_image(match.group(1).split()[0])

def process_consecutive_images(lines, current_idx, sender):
    """Process multiple consecutive image messages"""
    images = []
    caption = []
    i = current_idx
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        if not is_new_message(line):
            caption.append(line)
            i += 1
            continue
            
        match = re.match(r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2} - (.*?): (.*)", line)
        if not match or match.group(1) != sender:
            break
            
        message = match.group(2)
        if not is_attachment(message) or not is_image(message.split()[0]):
            break
            
        images.append(message.split()[0])
        i += 1
    
    caption_text = '<br>'.join(caption) if caption else ''
    return images, caption_text, i - current_idx

def format_message_text(text):
    """Enhanced version that handles URLs in multiline text"""
    url_pattern = r'(https?://\S+)'
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)

def is_audio_message(filename):
    """Check if the filename indicates an audio message"""
    return filename.startswith('AUD-') and filename.endswith('.')

def is_video(filename):
    """Check if the filename is a video file"""
    return filename.lower().endswith('.mp4')

def is_contact(filename):
    """Check if the filename is a contact card"""
    return filename.lower().endswith('.vcf')

def is_location_message(message_lines):
    """Check if the message is a location share"""
    if len(message_lines) >= 2:
        return message_lines[0].strip() == "location:" and "maps.google.com" in message_lines[1]
    return False

def is_deleted_message(message):
    """Check if the message was deleted"""
    return message in ["This message was deleted", "You deleted this message"]

def get_file_icon(filename):
    """Get the appropriate FontAwesome icon class for a file type"""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    return FILE_ICONS.get(ext, 'fas fa-file')

def process_consecutive_videos(lines, current_idx, sender):
    """Process multiple consecutive video messages"""
    videos = []
    caption = []
    i = current_idx
    
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        if not is_new_message(line):
            caption.append(line)
            i += 1
            continue
            
        match = re.match(r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2} - (.*?): (.*)", line)
        if not match or match.group(1) != sender:
            break
            
        message = match.group(2)
        if not is_attachment(message) or not is_video(message.split()[0]):
            break
            
        videos.append(message.split()[0])
        i += 1
    
    caption_text = '<br>'.join(caption) if caption else ''
    return videos, caption_text, i - current_idx

def count_messages(lines):
    """Count total number of messages in the chat"""
    count = 0
    for line in lines:
        if is_new_message(line):
            count += 1
    return count

def parse_whatsapp_chat(filename, user_name, date_format_override=None):
    """
    Parse WhatsApp chat with enhanced date handling and media omitted message handling
    date_format_override: Optional "US" or "EU" to force a specific format
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        # Count total messages
        total_messages = count_messages(lines)
            
        other_person = get_other_person_name(lines, user_name)
        
        # Detect date format from first valid message if not overridden
        detected_format = None
        if not date_format_override:
            for line in lines:
                match = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[APMapm]{2})", line)
                if match:
                    date_str = match.group(1)
                    _, detected_format = try_parse_date(date_str)
                    if detected_format:
                        break
        
        date_format = date_format_override or detected_format or "US"  # Default to US if detection fails
        
        html_output = f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>WhatsApp Chat</title>
    <link rel="stylesheet" href="media/files/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
<div class='chat-header'>
    <img src='media/receiver.jpg' alt='Profile Picture'>
    <div class='chat-header-info'>
        <div class='chat-header-name'>{other_person}</div>
        <div class='chat-header-status'>online</div>
    </div>
    <div class='chat-header-actions'>
        <i class='fas fa-video'></i>
        <i class='fas fa-phone'></i>
        <i class='fas fa-ellipsis-v'></i>
    </div>
</div>
<div class='chat-container'>\n"""
        
        current_date = None
        i = 0
        
        # Process encryption notice with enhanced date handling
        first_line = lines[0].strip()
        match = re.match(r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[APMapm]{2}) - (.*)", first_line)
        if match:
            date_str = match.group(1)
            parsed_date, _ = try_parse_date(date_str)
            if parsed_date:
                html_output += encryption_notice_template.format(
                    date=parsed_date.strftime("%m/%d/%Y"),
                    time=match.group(2)
                )
            i += 1

        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            if not is_new_message(line):
                i += 1
                continue
            
            # Enhanced date parsing in collect_full_message
            message_lines, date_str, time, sender, skip_lines = collect_full_message(lines, i)
            
            # Parse date with new flexible parser
            parsed_date, _ = try_parse_date(date_str)
            if not parsed_date:
                i += 1
                continue
            
            formatted_date = parsed_date.strftime("%m/%d/%Y")
            
            # Add date header if needed
            if formatted_date != current_date:
                current_date = formatted_date
                header_date = parsed_date.strftime("%B %d, %Y")
                html_output += date_header_template.format(formatted_date=header_date)
            
            message = message_lines[0]
            message_class = 'sender' if sender == user_name else 'receiver'
            read_receipt = ' <i class="fas fa-check-double" style="color: #4fc3f7;"></i>' if sender == user_name else ''
            
            # Handle media omitted messages
            if message.strip() == "<Media omitted>":
                template = outgoing_message_template if sender == user_name else incoming_message_template
                html_output += template.format(message_text="<Media omitted>", timestamp=time)
            else:
                # Rest of your existing message type handling code...
                if is_deleted_message(message):
                    html_output += deleted_message_template.format(
                        message_class=message_class,
                        deleted_text=message,
                        timestamp=time,
                        read_receipt=read_receipt
                    )
                
                elif is_location_message(message_lines):
                    map_url = message_lines[1].strip()
                    html_output += location_template.format(
                        message_class=message_class,
                        map_url=map_url,
                        timestamp=time,
                        read_receipt=read_receipt
                    )

                elif message == "null":
                    call_type = "Outgoing" if sender == user_name else "Incoming"
                    html_output += call_notification_template.format(call_type=call_type, timestamp=time)
                
                elif is_attachment(message):
                    filename = message.split()[0]
                    caption = '<br>'.join(message_lines[1:]) if len(message_lines) > 1 else ''
                    caption_html = f'<div class="file-caption">{caption}</div>' if caption else ''
                    
                    if is_video(filename):
                        if is_consecutive_video_start(lines, i):
                            videos, grid_caption, extra_skip = process_consecutive_videos(lines, i, sender)
                            skip_lines += extra_skip
                            
                            if len(videos) >= 4:
                                video_elements = '\n'.join(
                                    f'<video class="attachment" onclick="openLightbox(this.querySelector(\'source\').src)">'
                                    f'<source src="{vid}" type="video/mp4">'
                                    f'Your browser does not support the video tag.</video>' 
                                    for vid in videos
                                )
                                html_output += video_grid_template.format(
                                    message_class=message_class,
                                    video_elements=video_elements,
                                    caption_html=caption_html,
                                    timestamp=time,
                                    read_receipt=read_receipt
                                )
                            else:
                                html_output += video_template.format(
                                    message_class=message_class,
                                    video_path=filename,
                                    caption_html=caption_html,
                                    timestamp=time,
                                    read_receipt=read_receipt
                                )
                        
                        else:
                            html_output += video_template.format(
                                message_class=message_class,
                                video_path=filename,
                                caption_html=caption_html,
                                timestamp=time,
                                read_receipt=read_receipt
                            )
                    
                    elif is_audio_message(filename):
                        html_output += audio_message_template.format(
                            message_class=message_class,
                            audio_path=filename,
                            timestamp=time,
                            read_receipt=read_receipt
                        )
                    
                    elif is_contact(filename):
                        contact_name = filename.replace('.vcf', '')
                        html_output += contact_template.format(
                            message_class=message_class,
                            contact_name=contact_name,
                            contact_type="Contact card",
                            timestamp=time,
                            read_receipt=read_receipt
                        )
                    
                    elif filename.startswith('DOC-'):
                        icon_class = get_file_icon(filename)
                        file_type = filename.split('.')[-1].upper() if '.' in filename else 'N/A'
                        html_output += document_template.format(
                            message_class=message_class,
                            icon_class=icon_class,
                            filename=filename,
                            file_type=file_type,
                            file_size='9.99 MB',
                            caption_html=caption_html,
                            timestamp=time,
                            read_receipt=read_receipt
                        )
                    
                    else:
                        # Handle other existing attachment types (images, etc.)
                        if message == "null":
                            call_type = "Outgoing" if sender == user_name else "Incoming"
                            html_output += call_notification_template.format(call_type=call_type, timestamp=time)
                    
                        elif is_attachment(message):
                            filename = message.split()[0]
                            
                            if is_image(filename):
                                # Handle image attachment
                                caption = '<br>'.join(message_lines[1:]) if len(message_lines) > 1 else ''
                                if caption:
                                    caption = f'<div class="file-caption">{caption}</div>'
                                
                                if is_consecutive_image_start(lines, i):
                                    # Process multiple images
                                    images, grid_caption, extra_skip = process_consecutive_images(lines, i, sender)
                                    skip_lines += extra_skip
                                    
                                    if len(images) >= 4:
                                        image_elements = '\n'.join(
                                            f'<img src="{img}" alt="Image {idx+1}" onclick="openLightbox(this.src)">' 
                                            for idx, img in enumerate(images)
                                        )
                                        html_output += image_grid_template.format(
                                            message_class=message_class,
                                            image_elements=image_elements,
                                            caption_html=caption,
                                            timestamp=time,
                                            read_receipt=read_receipt
                                        )
                                    else:
                                        html_output += single_image_template.format(
                                            message_class=message_class,
                                            image_path=filename,
                                            caption_html=caption,
                                            timestamp=time,
                                            read_receipt=read_receipt
                                        )
                                else:
                                    html_output += single_image_template.format(
                                        message_class=message_class,
                                        image_path=filename,
                                        caption_html=caption,
                                        timestamp=time,
                                        read_receipt=read_receipt
                                    )
                                
                            elif is_voice_message(filename):
                                avatar_image = 'sender.jpg' if sender == user_name else 'receiver.jpg'
                                html_output += voice_message_template.format(
                                    message_class=message_class,
                                    avatar_image=avatar_image,
                                    audio_path=filename,
                                    timestamp=time,
                                    read_receipt=read_receipt
                                )
                
                else:
                    # Regular text message
                    full_message = '<br>'.join(line for line in message_lines if line)
                    formatted_message = format_message_text(full_message)
                    
                    template = outgoing_message_template if sender == user_name else incoming_message_template
                    html_output += template.format(message_text=formatted_message, timestamp=time)
            
            i += skip_lines

        html_output += f"""</div>
<div class="lightbox">
    <div class="lightbox-content">
        <img class="lightbox-content" style="display: none;">
        <video class="lightbox-content" controls style="display: none;">
            <source src="" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    <div class="lightbox-close" onclick="closeLightbox()">&times;</div>
</div>

<!-- Lightbox container -->
<div class='lightbox' onclick="closeLightbox()">
    <span class='lightbox-close'>&times;</span>
    <img class='lightbox-content'>
    <video class='lightbox-content' controls style="display: none;">
        <source src="" type="video/mp4">
    </video>
</div>
</div>
<script src="media/files/script.js"></script>
</body>
</html>"""
        
        # Generate output filename with message count
        output_filename = f"chat_output_{total_messages}.html"
        
        with open(output_filename, "w", encoding='utf-8') as html_file:
            html_file.write(html_output)
        
        print(f"HTML file generated successfully as '{output_filename}'.")
        print(f"Total messages processed: {total_messages}")
        if detected_format:
            print(f"Detected date format: {detected_format}")

    except FileNotFoundError:
        print("Error: .txt file not found in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

def is_consecutive_video_start(lines, current_idx):
    """Check if this is the start of consecutive videos"""
    if current_idx + 1 >= len(lines):
        return False
    next_line = lines[current_idx + 1].strip()
    if not is_new_message(next_line):
        return False
    match = re.match(r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APMapm]{2} - .*?: (.*)", next_line)
    return match and is_attachment(match.group(1)) and is_video(match.group(1).split()[0])

# Run the function
if __name__ == "__main__":
    user_name = input("Enter your name as it appears in the chat: ")
    format_choice = input("Enter date format (US for MM/DD/YY or EU for DD/MM/YY), or press Enter for auto-detect: ").upper()
    
    if format_choice in ["US", "EU"]:
        parse_whatsapp_chat("chat.txt", user_name, format_choice)
    else:
        parse_whatsapp_chat("chat.txt", user_name)