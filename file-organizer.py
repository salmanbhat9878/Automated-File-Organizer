from pathlib import Path
import shutil
import logging

FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov"],
    "Audio": [".mp3", ".wav", ".aac"],
    "Archives": [".zip", ".rar", ".7z"],
    "Code": [".py", ".html", ".css", ".js"]
}


def get_file_category(file_path):
    extension = file_path.suffix.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category
    return "Others"


def get_unique_filename(destination, reserved=None):
    if reserved is None:
        reserved = set()

    candidate = destination
    counter = 1

    while candidate.exists() or candidate in reserved:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        counter += 1

    return candidate


def organize_files(source_path, target_path, dry_run=True):
    source = Path(source_path).expanduser().resolve()
    target = Path(target_path).expanduser().resolve()

    if not source.is_dir():
        print("Error: Source folder does not exist!")
        return

    if source == target:
        print("Error: Source and target must be different.")
        return

    if source in target.parents or target in source.parents:
        print("Error: Use separate source and target folders.")
        return

    try:
        files = [
            file for file in source.iterdir()
            if file.is_file()
            and file.resolve() != Path(__file__).resolve()
        ]
    except OSError as error:
        print(f"Error reading folder: {error}")
        return

    if not files:
        print("No files found in the source folder.")
        return

    reserved = set()
    moved_count = 0

    for file_path in files:
        category = get_file_category(file_path)
        destination = target / category / file_path.name
        destination = get_unique_filename(destination, reserved)
        reserved.add(destination)

        if dry_run:
            print(
                f"[DRY RUN] {file_path.name} "
                f"-> {category}/{destination.name}"
            )
        else:
            try:
                destination.parent.mkdir(
                    parents=True, exist_ok=True
                )

                destination = get_unique_filename(destination)

                shutil.move(str(file_path), str(destination))

                print(
                    f"Moved: {file_path.name} "
                    f"-> {category}/{destination.name}"
                )

                logging.info(
                    "Moved %s to %s",
                    file_path,
                    destination
                )

                moved_count += 1

            except (OSError, shutil.Error) as error:
                print(f"Error moving {file_path.name}: {error}")
                logging.error(
                    "Error moving %s: %s",
                    file_path,
                    error
                )

    if dry_run:
        print(f"\nPreview complete: {len(files)} file(s).")
        print("No files were moved.")
    else:
        print(f"\nSuccessfully moved {moved_count} file(s).")


def main():
    logging.basicConfig(
        filename="organizer.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("=" * 40)
    print("       AUTOMATED FILE ORGANIZER")
    print("=" * 40)

    while True:
        print("\n1. Preview Files (Dry Run)")
        print("2. Organize Files")
        print("3. Exit")

        choice = input("Choose an option (1-3): ").strip()

        if choice == "3":
            print("Thank you for using File Organizer!")
            break

        elif choice in ["1", "2"]:
            source = input(
                "Enter source folder path: "
            ).strip().strip('"')

            target = input(
                "Enter target folder path: "
            ).strip().strip('"')

            if not source or not target:
                print("Please enter both folder paths.")
                continue

            if choice == "1":
                organize_files(source, target, dry_run=True)

            else:
                confirm = input(
                    "Files will be moved. Type YES to continue: "
                ).strip()

                if confirm == "YES":
                    organize_files(source, target, dry_run=False)
                else:
                    print("Operation cancelled.")

        else:
            print("Invalid choice! Please select 1-3.")


if __name__ == "__main__":
    main()