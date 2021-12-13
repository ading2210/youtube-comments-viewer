import requests, random, replit, urllib.parse
from flask import Flask, request, redirect
import pyyoutube

from datetime import datetime, timezone
from dateutil import parser

api = pyyoutube.Api(api_key=replit.db["key"])

app = Flask(__name__)

def errorPage(error):
  html = '''
    <title>An error occured</title>
    <h2>Error</h2>
    <code>{error}</code>
    '''.format(error=str(error))
  return html

def pretty_date(time=False, alternate=False, now=datetime.now(timezone.utc)):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    based on https://stackoverflow.com/a/1551394
    """
    if type(time) is int:
      diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
      diff = now - time
    elif not time:
      diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
      return 'just now'

    if day_diff == 0:
      if second_diff < 5:
          return "just now"
      if second_diff < 60:
        return str(round(second_diff)) + " seconds ago"
      if second_diff < 120:
        return "1 minute ago"
      if second_diff < 3600:
        return str(round(second_diff / 60)) + " minutes ago"
      if second_diff < 7200:
        return "1 hour ago"
      if second_diff < 86400:
        return str(round(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
      return "Yesterday"
    if alternate == False:
      if day_diff < 7:
        return str(round(day_diff)) + " days ago"
      if day_diff < 31:
        if round(day_diff / 7) == 1:
          return "1 week ago"
        return str(round(day_diff / 7)) + " weeks ago"
      if day_diff < 365:
        if round(day_diff / 30) == 1:
          return "1 month ago"
        return str(round(day_diff / 30)) + " months ago"
      if round(day_diff / 365) == 1:
        return "1 year ago"
      return str(round(day_diff / 365)) + " years ago"
    readableDate = time.strftime("%B %d, %Y")
    return readableDate

def updatedAfter(updatedAtIso, publishedAtIso):
  updatedAt = parser.parse(updatedAtIso)
  publishedAt = parser.parse(publishedAtIso)
  diff = publishedAt - updatedAt
  diffSeconds = diff.seconds

  if diffSeconds > 0:
    updatedAtDisplay = pretty_date(publishedAt,now=updatedAt)
    updatedAtDisplay = updatedAtDisplay.replace("ago","later").replace("Yesterday", "1 day later").replace("just now", "just after posting")
    updatedAtDisplay = " (Edited: "+updatedAtDisplay+")"
  else:
    updatedAtDisplay = ""

  return updatedAtDisplay

def videoHeader(video, videoId):
  videoUploader = api.get_channel_info(channel_id=video.snippet.channelId).items[0]
  title = video.snippet.title
  id = videoId
  videoPublishedDate = pretty_date(parser.parse(video.snippet.publishedAt), alternate=True)
  views = format(int(video.statistics.viewCount), ",")
  videoUploaderTitle = videoUploader.snippet.title

  videoUploaderUrl = videoUploader.snippet.customUrl
  if videoUploaderUrl == None:
    videoUploaderUrl = "channel/"+video.snippet.channelId
  videoUploaderUrl = "https://youtube.com/" + videoUploaderUrl

  videoUploaderProfile = videoUploader.snippet.thumbnails.high.url
  videoUploaderSubscribers = format(int(videoUploader.statistics.subscriberCount), ",")

  likeCount = format(int(video.statistics.likeCount), ",")
  #RIP Youtube dislikes...
  #dislikeCount = format(int(video.statistics.dislikeCount), ",")

  html = '''
    <style>
    .videoLikeData {
      display: flex;
      align-items: center;
      font-size: 13px;
      height: 16px;
      margin-top: 3px;
      margin-bottom: 3px;
    }
    </style>
  '''

  html = html + '''
  <title>Comments for: {videoTitle}</title>
  <link rel="icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABRElEQVR42u2Wuw3CMBCGvQELIMEI6WgiwQZkA7IBbJBUtDACEyA2gA2IsgAwAdRpfvgVE14J2LEJFD7pOp/v8/leAj8W4QAcgPLJ/R7YbN5rklgC4EW8cDIBut3LKaGvtKP9apXDfwQ4HIBeD2i36zlUAYpj4HSqAPD97zguU0blAYDhVjFcLoHp1A6EjEQOEASfDfr9W9x2O2A4NAPgowuAwUAP4CqzGdBq1QNgPhgDUI5HYDTSBykAFgs1gyqA+2/pdGoAsFZtAFCiqAZAGNoB2G71vmE+lwBpagawXucVoZsDRRWo9oDx+NU5k8+4DPkXKgZ0RsmyW+ab9AE5H9SrwKbKBMwB2BKbdM6uezeQRDF+m3DueS87g3hYOFQ6oonzp1FcvpCwPm2C8C5Z8/or2fPKVfKCyrNXdVuxA3AA/w5wBviNiB8PHAZ4AAAAAElFTkSuQmCC" type="image/png">
  '''.format(videoTitle=title)

  html = html + '''
  <table>
    <tr>
      <td>
        <img src="https://img.youtube.com/vi/{id}/mqdefault.jpg" alt="Thumbnail" height=128px>
      </td>
      <td class="tableData">
        <a href="https://youtube.com/watch?v={id}" style="font-size:20px">{title}</a>
        <p style="font-size:14px; margin-top:2px; margin-bottom:2px ">{views} views - Uploaded: {videoPublishedDate}</p>

        <div class="videoLikeData">
          <svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" class="likeIcon" style="pointer-events: none; display: block; width: 24px; height: 24px"><g><path d="M18.77,11h-4.23l1.52-4.94C16.38,5.03,15.54,4,14.38,4c-0.58,0-1.14,0.24-1.52,0.65L7,11H3v10h4h1h9.43 c1.06,0,1.98-0.67,2.19-1.61l1.34-6C21.23,12.15,20.18,11,18.77,11z M7,20H4v-8h3V20z M19.98,13.17l-1.34,6 C18.54,19.65,18.03,20,17.43,20H8v-8.61l5.6-6.06C13.79,5.12,14.08,5,14.38,5c0.26,0,0.5,0.11,0.63,0.3 c0.07,0.1,0.15,0.26,0.09,0.47l-1.52,4.94L13.18,12h1.35h4.23c0.41,0,0.8,0.17,1.03,0.46C19.92,12.61,20.05,12.86,19.98,13.17z"></path></g></svg>
          <p style="margin-right:5px">{likeCount}</p>
        </div>

        <table style="margin-left: 0px; margin-top:4px; border-collapse: collapse">
          <tr>
            <td class="tableData" style="margin-left: 0px">
              <div>
                <img src="{videoUploaderProfile}" alt="video uploader" style="width:48px;height:48px;">
              <div>
            </td>
            <td class="tableData">
              <div class=commentHeader>
                <a href="{videoUploaderUrl}" target="_blank">{videoUploaderTitle}</a>
                <p style="font-size:12px; margin-top:2px; margin-bottom:2px ">Subscribers: {videoUploaderSubscribers}</p>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
  <hr style="margin-top:2px; margin-bottom:5px">
  '''.format(id=id,title=title, views=views, videoPublishedDate=videoPublishedDate, videoUploaderTitle=videoUploaderTitle, videoUploaderProfile=videoUploaderProfile, videoUploaderUrl=videoUploaderUrl, videoUploaderSubscribers=videoUploaderSubscribers,likeCount=likeCount, dislikeCount=dislikeCount)

  return html

@app.route('/')
def homepage():
  html = '''
  <!DOCTYPE html>

  <head>
    <title>Youtube Comments Viewer</title>
    <link rel="icon" href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABRElEQVR42u2Wuw3CMBCGvQELIMEI6WgiwQZkA7IBbJBUtDACEyA2gA2IsgAwAdRpfvgVE14J2LEJFD7pOp/v8/leAj8W4QAcgPLJ/R7YbN5rklgC4EW8cDIBut3LKaGvtKP9apXDfwQ4HIBeD2i36zlUAYpj4HSqAPD97zguU0blAYDhVjFcLoHp1A6EjEQOEASfDfr9W9x2O2A4NAPgowuAwUAP4CqzGdBq1QNgPhgDUI5HYDTSBykAFgs1gyqA+2/pdGoAsFZtAFCiqAZAGNoB2G71vmE+lwBpagawXucVoZsDRRWo9oDx+NU5k8+4DPkXKgZ0RsmyW+ab9AE5H9SrwKbKBMwB2BKbdM6uezeQRDF+m3DueS87g3hYOFQ6oonzp1FcvpCwPm2C8C5Z8/or2fPKVfKCyrNXdVuxA3AA/w5wBviNiB8PHAZ4AAAAAElFTkSuQmCC" type="image/png">
    <style>
      * {
        font-family: Arial;
      }
      .mainDiv {
        height: 50%;
        width: 50%;
        text-align: center;
        margin: auto;
      }
    </style>
  </head>

  <div class="mainDiv">
    <h2>Youtube Comments Viewer</h2>
    <img src="/static/images/screenshot1.png" alt="screenshot of page" width=400px>
    <form method="POST">
      <p><input class="textInput" name="text" placeholder="Youtube URL"><input type="submit"></p>
      <p style="font-size: 12px">Enter the URL of a Youtube video to view its comments.</p>
    </form>
    <hr>
    <h3>Add this bookmarklet for easy access to this page!</h3>
    <a href='javascript: function getParameterByName(e,n=window.location.href){e=e.replace(/[\[\]]/g,"\\$&");var t=new RegExp("[?&]"+e+"(=([^&#]*)|&|#|$)").exec(n);return t?t[2]?decodeURIComponent(t[2].replace(/\+/g," ")):"":null}var id=getParameterByName("v");null!=id&&window.open("https://youtube-comments-fetcher.uniqueostrich18.repl.co/comments?id="+id);' target="_parent"><button>Get Youtube Comments</button></a>
    <p style="font-size: 12px">Drag this into your bookmarks bar to add it. You can click it when on a youtube video to instantly open the comments.</p>
  </div>
  '''
  return html

@app.route("/", methods=['POST'])
def form():
  try:
    videoString = request.form['text']
    urlData = urllib.parse.urlparse(videoString)
    query = urllib.parse.parse_qs(urlData.query)
    videoId = query["v"][0]
    return redirect("/comments?id="+videoId, code=302)
  except:
    return errorPage("Could not get video ID.")

@app.route("/static/<path:path>")
def serveStaticFile(path):
  return send_from_directory("static", path)

@app.route('/comments')
def comments():
  id = request.args.get("id")
  page = request.args.get("page")
  order = request.args.get("order")

  if order == None:
    order = "relevance"

  try:
    if not page == None:
      commentThreadsRaw = api.get_comment_threads(video_id=id, count=30, order=order,page_token=page)
    else:
      commentThreadsRaw = api.get_comment_threads(video_id=id, count=30, order=order)
    commentThreads = commentThreadsRaw.items
    commentIds = []
    for commentThread in commentThreads:
      commentIds.append(commentThread.id)
    commentIdsString = ",".join(commentIds)

    video = api.get_video_by_id(video_id=id).items[0]

  except pyyoutube.error.PyYouTubeException as e:
    return errorPage(e)

  comments = api.get_comment_by_id(comment_id=commentIdsString).items

  html = '''
  <!DOCTYPE html>

  <style>
    * {
      font-family: Arial;
    }
    .tableData {
      vertical-align: top;
      line-height: 1.2;
    }
    .commentText {
      padding-top: 3px;
      margin-top: 0px;
      padding-bottom: 6px;
      margin-bottom: 0px;
      word-break: break-word;
    }
    .likeData {
      display: flex;
      align-items: center;
      font-size: 13px;
      height: 16px
    }
    .commentHeader {
      display: inline-block;
    }
    .header {
      display: inline-block;
      margin-top: 0px;
      margin-bottom: 0px;
    }
    .noVerticalMargin {
      margin-top: 0px;
      margin-bottom: 0px;
    }
  </style>
  '''

  commentCount = video.statistics.commentCount
  if not commentCount == 1:
    commentCountReadable = commentCount = format(int(video.statistics.commentCount), ",") + " comments"
  else:
    commentCountReadable = str(commentCount) + " comment"

  html = html + videoHeader(video, id)
  html = html + '''
  <p style="margin-top: 4px; margin-bottom: 4px"><a href="/">← Go Back</a> | {commentCountReadable} | Sort by: <a href="/comments?id={id}">Top</a> / <a href="/comments?id={id}&order=time">New</a></p>
  <hr style="margin-top:5px; margin-bottom:5px"> 
  '''.format(id=id, commentCountReadable=commentCountReadable)

  counter = 0
  for comment in comments:
    commentThread = commentThreads[counter]
    profile = comment.snippet.authorProfileImageUrl
    author = comment.snippet.authorDisplayName
    authorUrl = comment.snippet.authorChannelUrl
    text = comment.snippet.textDisplay
    likeCount = format(int(comment.snippet.likeCount), ",")
    replies = commentThread.snippet.totalReplyCount
    commentId = comment.id
    publishedAtIso = comment.snippet.publishedAt
    publishedAtFriendly = pretty_date(parser.parse(publishedAtIso))
    updatedAtIso = comment.snippet.updatedAt

    updatedAtDisplay = updatedAfter(updatedAtIso,publishedAtIso)

    html = html + '''
    <table style="max-width:50%">
      <tr>
        <td class="tableData">
          <div>
            <img src="{profile}" alt="{author}" style="width:64px;height:64px;">
          </div>
        </td>
        <td class="tableData">
          <div class=commentHeader>
            <a href="{authorUrl}" target="_blank">{author}</a>
          </div>
          <div class=commentHeader style="height: 0px">
            <p style="font-size:12px; margin: 0px">Published: {publishedAt}{updatedAtDisplay}</p>
          </div>
          <p class="commentText">{content}</p>

          <div class="likeData">
            <svg viewBox="0 0 16 16" focusable="false" style="pointer-events: none; display: block; width: 16px; height: 16px;"><g><path d="M12.42,14A1.54,1.54,0,0,0,14,12.87l1-4.24C15.12,7.76,15,7,14,7H10l1.48-3.54A1.17,1.17,0,0,0,10.24,2a1.49,1.49,0,0,0-1.08.46L5,7H1v7ZM9.89,3.14A.48.48,0,0,1,10.24,3a.29.29,0,0,1,.23.09S9,6.61,9,6.61L8.46,8H14c0,.08-1,4.65-1,4.65a.58.58,0,0,1-.58.35H6V7.39ZM2,8H5v5H2Z"></path></g></svg>
            <p style="padding-left:3px">{likeCount}</p>
            <a href="/replies?id={commentId}&videoId={id}" style="padding-left:10px">Replies: {replies}</a>
          </div>
        </td>
      </tr>
    </table>
    '''.format(
      content=text, profile=profile, author=author, authorUrl=authorUrl, likeCount=likeCount, replies=replies, commentId=commentId, publishedAt=publishedAtFriendly, id=id, updatedAtDisplay=updatedAtDisplay)
    counter = counter+1

  html = html + '''
  <hr>
  <p class="noVerticalMargin">
  '''

  prevPageToken = commentThreadsRaw.prevPageToken
  nextPageToken = commentThreadsRaw.nextPageToken

  if type(prevPageToken) is str:
    html = html + '''
    <a href="/comments?id={id}&order={order}&page={page}">Previous Page</a>
    '''.format(id=id, page=prevPageToken, order=order)
  elif not page == None:
    html = html + '''
    <a href="javascript:history.back()">Previous Page</a>
    '''
  
  if nextPageToken != None and type(prevPageToken) is str or page != None:
    html = html + '''
     / 
    '''

  if type(nextPageToken) is str:
    html = html + '''
    <a href="/comments?id={id}&order={order}&page={page}">Next Page</a>
    '''.format(id=id, page=nextPageToken, order=order)

  html = html + '''
  </p>
  '''

  return html

@app.route("/replies")
def replies():
  id = request.args.get("id")
  page = request.args.get("page")
  videoId = request.args.get("videoId")
  try:
    if not page == None:
      commentsRaw = api.get_comments(parent_id=id, count=500, limit=500, page_token=page)
    else:
      commentsRaw = api.get_comments(parent_id=id, count=500, limit=500)
    comments = commentsRaw.items
    nextPageToken = commentsRaw.nextPageToken
    print(len(comments))

    parent = api.get_comment_by_id(comment_id=id).items[0]

    if not videoId == None:
      video = api.get_video_by_id(video_id=videoId).items[0]
  except pyyoutube.error.PyYouTubeException as e:
    return errorPage(e)

  html = '''
  <!DOCTYPE html>

  <style>
    * {
      font-family: Arial;
    }
    .tableData {
      vertical-align:top;
      line-height: 1.2;
    }
    .commentText {
      padding-top: 3px;
      margin-top: 0px;
      padding-bottom: 6px;
      margin-bottom: 0px;
    }
    .likeData {
      display: flex;
      align-items: center;
      font-size: 13px;
      height: 16px
    }
    .commentHeader {
      display: inline-block;
    }
    .noVerticalMargin {
      margin-top: 0px;
      margin-bottom: 0px;
    }
  </style>
  '''

  if not videoId == None:
    html = html + videoHeader(video, videoId)

  parentPublishedAtIso = parent.snippet.publishedAt
  parentPublishedAtFriendly = pretty_date(parser.parse(parentPublishedAtIso))
  parentLikes = format(int(parent.snippet.likeCount), ",")

  parentUpdatedAtIso = parent.snippet.updatedAt

  updatedAtDisplay = updatedAfter(parentUpdatedAtIso,parentPublishedAtIso)

  html = html + '''
    <p style="margin-top: 4px; margin-bottom: 4px"><a href="javascript:history.back()">← Go Back</a> | You are viewing replies.</p>
    <hr style="margin-top:5px; margin-bottom:5px">
    <table style="max-width:60%">
      <tr>
        <td class="tableData">
          <div>
            <img src="{profile}" alt="{author}" style="width:96px;height:96px;">
          </div>
        </td>
        <td class="tableData">
          <div class=commentHeader>
            <a href="{authorUrl}" target="_blank">{author}</a>
          </div>
          <div class=commentHeader style="height: 0px">
            <p style="font-size:12px; margin: 0px">Published: {publishedAt}{updatedAtDisplay}</p>
          </div>
          <p class="commentText">{content}</p>

          <div class="likeData">
            <svg viewBox="0 0 16 16" focusable="false" style="pointer-events: none; display: block; width: 16px; height: 16px;"><g><path d="M12.42,14A1.54,1.54,0,0,0,14,12.87l1-4.24C15.12,7.76,15,7,14,7H10l1.48-3.54A1.17,1.17,0,0,0,10.24,2a1.49,1.49,0,0,0-1.08.46L5,7H1v7ZM9.89,3.14A.48.48,0,0,1,10.24,3a.29.29,0,0,1,.23.09S9,6.61,9,6.61L8.46,8H14c0,.08-1,4.65-1,4.65a.58.58,0,0,1-.58.35H6V7.39ZM2,8H5v5H2Z"></path></g></svg>
            <p style="padding-left:3px">{likeCount}</p>
          </div>
        </td>
      </tr>
    </table>
    '''.format(
      content=parent.snippet.textDisplay, profile=parent.snippet.authorProfileImageUrl, author=parent.snippet.authorDisplayName, authorUrl=parent.snippet.authorChannelUrl, likeCount=parentLikes, publishedAt=parentPublishedAtFriendly,updatedAtDisplay=updatedAtDisplay)

  for i in range(len(comments)-1,-1, -1):
    comment = comments[i]
    profile = comment.snippet.authorProfileImageUrl
    author = comment.snippet.authorDisplayName
    authorUrl = comment.snippet.authorChannelUrl
    text = comment.snippet.textDisplay
    likeCount = format(int(comment.snippet.likeCount), ",")
    publishedAtIso = comment.snippet.publishedAt
    publishedAtFriendly = pretty_date(parser.parse(publishedAtIso))

    updatedAtIso = comment.snippet.updatedAt
    updatedAtDisplay = updatedAfter(updatedAtIso,publishedAtIso)

    html = html + '''
    <table style="max-width:50%">
      <tr>
        <td class="tableData">
          <div>
            <img src="{profile}" alt="{author}" style="width:64px;height:64px;">
          </div>
        </td>
        <td class="tableData">
          <div class=commentHeader>
            <a href="{authorUrl}" target="_blank">{author}</a>
          </div>
          <div class=commentHeader style="height: 0px">
            <p style="font-size:12px; margin: 0px">Published: {publishedAt}{updatedAtDisplay}</p>
          </div>
          <p class="commentText">{content}</p>

          <div class="likeData">
            <svg viewBox="0 0 16 16" focusable="false" style="pointer-events: none; display: block; width: 16px; height: 16px;"><g><path d="M12.42,14A1.54,1.54,0,0,0,14,12.87l1-4.24C15.12,7.76,15,7,14,7H10l1.48-3.54A1.17,1.17,0,0,0,10.24,2a1.49,1.49,0,0,0-1.08.46L5,7H1v7ZM9.89,3.14A.48.48,0,0,1,10.24,3a.29.29,0,0,1,.23.09S9,6.61,9,6.61L8.46,8H14c0,.08-1,4.65-1,4.65a.58.58,0,0,1-.58.35H6V7.39ZM2,8H5v5H2Z"></path></g></svg>
            <p style="padding-left:3px">{likeCount}</p>
          </div>
        </td>
      </tr>
    </table>
    '''.format(
      content=text, profile=profile, author=author, authorUrl=authorUrl, likeCount=likeCount, publishedAt=publishedAtFriendly,updatedAtDisplay=updatedAtDisplay)

  prevPageToken = commentsRaw.prevPageToken
  if not videoId == None:
    videoIdString = "&videoId="+videoId
  else:
    videoIdString = ""
  if type(prevPageToken) is str:
    html = html + '''
    <a href="/replies?id={id}&page={page}">Previous Page</a>
    '''.format(id=id, page=prevPageToken, videoIdString=videoIdString)
  elif not page == None:
    html = html + '''
    <a href="javascript:history.back()">Previous Page</a>
    '''  
  if type(nextPageToken) is str:
    html = html + '''
    <a href="/replies?id={id}&page={page}{videoIdString}">Next Page</a>
    '''.format(id=id, page=nextPageToken,videoIdString=videoIdString)

  return html

@app.route('/json')
def getJson():
  id = request.args.get("v")
  order = request.args.get("order")

  if order == None:
    order = "relevance"

  commentThreads = api.get_comment_threads(video_id="dQw4w9WgXcQ", count=30, order=order,return_json=True)
  return commentThreads

if __name__ == '__main__':
  app.run(host='0.0.0.0')