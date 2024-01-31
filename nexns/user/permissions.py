from typing import TYPE_CHECKING
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

if TYPE_CHECKING:
    from .lib.scope import ApiKeyScope


class IsAuthenticatedUser(BasePermission):
    
    def has_permission(self, request, view):
        return not request.is_apikey_auth and request.user and request.user.is_authenticated


class IsAuthenticatedApiKey(BasePermission):

    def has_permission(self, request, view):
        return request.is_apikey_auth


class IsSuperUser(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class ApiKeyDomainPermission(BasePermission):

    def has_permission(self, request, view):
        action = view.action
        pk = view.kwargs.get('pk', None)
        scope: 'ApiKeyScope' = request.apikey_scope

        if action == 'list':
            return scope.can_read_domains
        
        elif action == 'create':
            return scope.can_create_domains
        
        elif action == 'retrieve':
            return scope.can_read_domains or pk in scope.can_read_specific_domains
              
        elif action == 'update' or action == 'partial_update':
            return scope.can_modify_domains or pk in scope.can_modify_specific_domains
        
        elif action == 'destroy':
            return scope.can_delete_domains
        
        elif action == 'apply':
            return scope.can_apply_domains or pk in scope.can_apply_specific_domains
        

class ApiKeyZonePermission(BasePermission):

    def has_permission(self, request, view):
        action = view.action
        pk = view.kwargs.get('pk', None)
        scope: 'ApiKeyScope' = request.apikey_scope

        if action == 'list':
            return scope.can_read_domains
        
        elif action == 'create':
            return scope.can_create_domains
        
        elif action == 'retrieve':
            return scope.can_read_domains or pk in scope.can_read_specific_zones
              
        elif action == 'update' or action == 'partial_update':
            return scope.can_modify_domains or pk in scope.can_modify_specific_zones
        
        elif action == 'destroy':
            return scope.can_delete_domains
        

class ApiKeyRRsetPermission(BasePermission):

    def has_permission(self, request, view):
        action = view.action
        pk = view.kwargs.get('pk', None)
        scope: 'ApiKeyScope' = request.apikey_scope

        if action == 'list':
            return scope.can_read_domains
        
        elif action == 'create':
            return scope.can_create_domains
        
        elif action == 'retrieve':
            return scope.can_read_domains or pk in scope.can_read_specific_rrsets
              
        elif action == 'update' or action == 'partial_update':
            return scope.can_modify_domains or pk in scope.can_modify_specific_rrsets
        
        elif action == 'destroy':
            return scope.can_delete_domains


class ApiKeyRecordPermission(BasePermission):

    def has_permission(self, request, view):
        action = view.action
        pk = view.kwargs.get('pk', None)
        scope: 'ApiKeyScope' = request.apikey_scope

        if action == 'list':
            return scope.can_read_domains
        
        elif action == 'create':
            return scope.can_create_domains
        
        elif action == 'retrieve':
            return scope.can_read_domains or pk in scope.can_read_specific_records
              
        elif action == 'update' or action == 'partial_update':
            return scope.can_modify_domains or pk in scope.can_modify_specific_records
        
        elif action == 'destroy':
            return scope.can_delete_domains
        

class ApiKeyVariablePermission(BasePermission):

    def has_permission(self, request, view):
        action = view.action
        pk = view.kwargs.get('pk', None)
        scope: 'ApiKeyScope' = request.apikey_scope

        if action == 'list':
            return scope.can_read_variables
        
        elif action == 'create':
            return scope.can_create_variables
        
        elif action == 'retrieve':
            return scope.can_read_variables or pk in scope.can_read_specific_variables
              
        elif action == 'update' or action == 'partial_update':
            return scope.can_modify_variables or pk in scope.can_modify_specific_variables
        
        elif action == 'destroy':
            return scope.can_delete_variables


def check_domain_user(request, domain):
    if domain.user.id != request.user.id:
        raise PermissionDenied('You have not enough permission to perform this action.')
