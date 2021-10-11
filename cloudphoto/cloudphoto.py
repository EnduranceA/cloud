import argparse
import configparser
import os
import boto3 as boto3


# ОТПРАВКА ФОТОГРАФИЙ В ОБЛАЧНОЕ ХРАНИЛИЩЕ
def upload_photos(path, album):
    # проверяем существование каталога
    if os.path.exists(path):
        album_name = album + '/'
        # проверяем существование альбома в облачном хранилище
        if check_album(album) is False:
            client.put_object(Bucket=bucket, Key=album_name)

        for filename in os.listdir(path):
            if filename.endswith(".jpg") or filename.endswith(".jpeg"):
                client.upload_file(path + '\\' + filename, bucket, album_name + filename)
                continue
    else:
        print(FileExistsError('Каталога ' + path + ' не существует'))


# ЗАГРУЗКА ФОТОГРАФИЙ НА КОМПЬЮТЕР
def download_photos(path, album):
    # проверяем существование каталога
    if os.path.exists(path):
        # проверяем существование альбома в облачном хранилище
        if check_album(album):
            os.chdir(path)
            photos = client.list_objects(Bucket=bucket, Prefix=album + '/')['Contents']
            for photo in photos:
                name = str(photo['Key']).split('/')[1]
                if name != '':
                    with open(name, 'wb') as data:
                        client.download_fileobj(Bucket=bucket, Key=photo['Key'], Fileobj=data)
        # если такого каталога нет, возвращаем ошибку
        else:
            print(Exception('Альбома ' + album + ' не существует'))
    else:
        print(FileExistsError('Каталога ' + path + ' не существует'))


# ПРОСМОТР СПИСКА АЛЬБОМОВ
def view_albums():
    files = client.list_objects(Bucket=bucket, MaxKeys=20)['Contents']
    for file in files:
        response = client.head_object(Bucket=bucket, Key=file['Key'])
        if response['ContentLength'] == 0:
            print(file['Key'])


# ПРОСМОТР СПИСКА ФОТОГРАФИЙ В АЛЬБОМЕ
def view_photos_album(album):
    album_name = album + '/'
    # проверяем существование альбома в облачном хранилище
    if check_album(album):
        photos = client.list_objects(Bucket=bucket, Prefix=album_name, MaxKeys=20)['Contents']
        for photo in photos:
            print(photo['Key'])
    else:
        # если такого каталога нет, то возвращаем ошибку
        print(Exception('Альбома ' + album + ' не существует'))


def check_album(album):
    response = client.list_objects(Bucket=bucket)['Contents']
    for file in response:
        folder = file['Key'].split('/')[0]
        if album == folder:
            return True
    return False


if __name__ == '__main__':
    cfg = configparser.ConfigParser()
    cfg.read('settings.ini')

    bucket = cfg['yandex.cloud']['bucket_name']
    secret_key = cfg['AWS4']['aws_secret_access_key']
    key_id = cfg['AWS4']['aws_access_key_id']

    session = boto3.Session(
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
    )

    client = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
    )
    """ :type: pyboto3.s3 """

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='command')

    # список команда
    upload = subparser.add_parser('upload')
    download = subparser.add_parser('download')
    list = subparser.add_parser('list')

    # аргументы для команды upload
    upload.add_argument('--p', type=str, required=True)
    upload.add_argument('--a', type=str, required=True)

    # аргументы для команды download
    download.add_argument('--p', type=str, required=True)
    download.add_argument('--a', type=str, required=True)

    # (необязательный) аргумент для команды list
    list.add_argument('--a', type=str, required=False)

    args = parser.parse_args()
    if args.command == 'upload':
        upload_photos(args.p, args.a)
    elif args.command == 'download':
        download_photos(args.p, args.a)
    elif args.command == 'list':
        if args.a is None:
            view_albums()
        else:
            view_photos_album(args.a)
