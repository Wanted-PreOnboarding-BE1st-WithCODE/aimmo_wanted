# aimmo_wanted

<br>

## [배포주소](url)
[url](url)

<br>

## 팀 구성
김민호 - 회원가입/로그인 구현(users app)<br>
박치훈 - 댓글 CRUD   (postings app에서 게시글과 댓글 함께 작성) <br>
이기용 - 게시글 CRUD (postings app에서 게시글과 댓글 함께 작성)

<br>

## 구현사항 상세

<br>

### 회원가입
- 정규표현식을 통해 이메일과 비밀번호 유효성 검사를 하고, 유효한 값일 때만 유저가 생성되게 했습니다.<br>
  (비밀번호 조건 : 8자 이상 / 최소 하나의 문자, 숫자, 특수문자)

- bcrypt를 사용하여 비밀번호를 암호화 저장할 수 있게 했습니다.

- Unit Test

### 로그인 

- 로그인 시, jwt 토큰이 발행됩니다.

- Unit Test

### 게시글 작성

- 로그인 유저만 가능합니다.

- Unit Test

### 검색을 통한 게시글 리스트 조회

- 특정 키워드를 입력하여 검색할 때, 검색 단어는 Query Parameter로 받으며 <br> 제목 혹은 내용에 해당 글자가 들어가는 게시글 리스트를 조회합니다.

- Unit Test

### 특정 게시글 조회

- Path Parmameter로 게시글 ID를 식별하여 조회합니다.

- 로그인한 유저가 이미 조회를 한 게시물이라면 조회수가 안 오르도록 설정하였습니다.

- Unit Test


### 게시글 수정

- Path Parmameter로 게시글 ID를 식별하여 수정합니다.

- 해당 게시물을 작성한 유저만 수정 가능하며, 일괄 수정이 아닌 일부 수정도 가능하게 설정하였습니다.

- HTTP method의 경우, POST를 이용하였습니다.

- Unit Test

### 게시글 삭제

- Path Parmameter로 게시글 ID를 식별하여 삭제합니다.

- Unit Test

## 기술스택

python, django, djongo
