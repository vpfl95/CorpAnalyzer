# 프로젝트 이름

## 소개
이 프로젝트는 [프로젝트에 대한 간단한 설명을 여기에 작성하세요].

## Git Hooks 설정

이 프로젝트는 일관된 코드 품질과 커밋 메시지 형식을 유지하기 위해 Git hooks를 사용합니다. 

### 자동 설정

프로젝트를 클론하고 pull을 받을 때마다 Git hooks가 자동으로 설정되고 업데이트됩니다. 별도의 설정이 필요하지 않습니다.

### 수동 설정 (필요한 경우)

만약 Git hooks가 자동으로 설정되지 않았다면, 다음 명령어를 실행하여 수동으로 설정할 수 있습니다:

```bash
bash setup-git-hooks.sh
```

### 커밋 메시지 규칙

모든 커밋 메시지는 다음 형식을 따라야 합니다:

```
type: subject
```

- `type`은 다음 중 하나여야 합니다: feat, fix, docs, style, refactor, test, chore
- `subject`는 변경사항에 대한 간단한 설명이어야 하며, 50자를 넘지 않아야 합니다.

예시:
- `feat: 사용자 로그인 기능 추가`
- `fix: 홈페이지 로딩 속도 개선`
- `docs: README 파일 업데이트`

이 규칙을 따르지 않는 커밋은 자동으로 거부됩니다.